import ipaddress
import socket
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import httpx

from app.config.settings import (
    WEB_READ_MAX_BYTES,
    WEB_READ_TIMEOUT_SECONDS,
)
from app.tools.errors import WebToolError


_ALLOWED_CONTENT_TYPES = (
    "text/",
    "application/xhtml+xml",
    "application/xml",
)
_REDIRECT_STATUS_CODES = {301, 302, 303, 307, 308}
_MAX_REDIRECTS = 3

_IGNORED_TAGS = {
    "aside",
    "form",
    "footer",
    "head",
    "header",
    "nav",
    "noscript",
    "script",
    "style",
}

_CONTAINER_TAGS = {
    "article",
    "main",
    "section",
    "div",
}

_BLOCK_TAGS = {
    "article",
    "blockquote",
    "br",
    "div",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "li",
    "main",
    "p",
    "pre",
    "section",
    "td",
    "th",
}

_POSITIVE_HINTS = {
    "article",
    "body",
    "content",
    "entry",
    "insight",
    "main",
    "post",
    "story",
}

_NEGATIVE_HINTS = {
    "banner",
    "breadcrumb",
    "cookie",
    "footer",
    "header",
    "menu",
    "nav",
    "newsletter",
    "promo",
    "related",
    "share",
    "sidebar",
    "social",
}

_MIN_DENSITY_TEXT_CHARS = 300


@dataclass
class _CandidateBlock:
    tag: str
    attrs_text: str
    parts: list[str] = field(default_factory=list)
    paragraph_count: int = 0
    heading_count: int = 0
    list_item_count: int = 0
    link_text_chars: int = 0

    def add_text(self, text: str, *, inside_link: bool) -> None:
        self.parts.append(text)

        if inside_link:
            self.link_text_chars += len(text)

    def add_boundary(self) -> None:
        self.parts.append("\n")

    def rendered_text(self) -> str:
        lines: list[str] = []
        current_line: list[str] = []

        def flush_line() -> None:
            if not current_line:
                return

            line = " ".join(current_line).strip()
            current_line.clear()

            if line:
                lines.append(line)

        for part in self.parts:
            if part == "\n":
                flush_line()
                continue

            current_line.append(part)

        flush_line()
        return "\n".join(lines).strip()

    def score(self) -> float:
        text = self.rendered_text()
        text_chars = len(text)

        if text_chars < _MIN_DENSITY_TEXT_CHARS:
            return float("-inf")

        link_ratio = self.link_text_chars / max(text_chars, 1)

        score = float(text_chars)
        score += self.paragraph_count * 140
        score += self.heading_count * 90

        score -= link_ratio * text_chars * 2.5
        score -= self.list_item_count * 45

        hints = {
            token
            for token in self.attrs_text.lower().replace("_", "-").split("-")
            if token
        }

        if self.tag == "article":
            score += 1200
        elif self.tag == "main":
            score += 900

        if any(hint in self.attrs_text.lower() for hint in _POSITIVE_HINTS):
            score += 500

        if any(hint in self.attrs_text.lower() for hint in _NEGATIVE_HINTS):
            score -= 1500

        if link_ratio >= 0.60:
            score -= 2500
        elif link_ratio >= 0.40:
            score -= 1200

        return score


class _ContentDensityExtractor(HTMLParser):
    """
    Deterministic main-content extractor.

    Strategy:
    - Ignore known boilerplate containers.
    - Build text-density candidates from article/main/section/div blocks.
    - Prefer long, paragraph-rich, low-link-density blocks.
    - Penalize menu/navigation-like structures.
    - Fall back to visible <body> text when no useful candidate exists.
    """

    def __init__(self) -> None:
        super().__init__()

        self._ignored_depth = 0
        self._link_depth = 0
        self._body_depth = 0

        self._candidate_stack: list[_CandidateBlock] = []
        self._completed_candidates: list[_CandidateBlock] = []
        self._fallback_parts: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        normalized = tag.lower()

        if normalized in _IGNORED_TAGS:
            self._ignored_depth += 1
            return

        if self._ignored_depth > 0:
            return

        if normalized == "body":
            self._body_depth += 1

        if normalized == "a":
            self._link_depth += 1

        if normalized in _CONTAINER_TAGS:
            attrs_text = " ".join(
                value or ""
                for key, value in attrs
                if key.lower() in {"id", "class", "role"}
            )
            self._candidate_stack.append(
                _CandidateBlock(
                    tag=normalized,
                    attrs_text=attrs_text,
                )
            )

        if normalized == "p":
            for candidate in self._candidate_stack:
                candidate.paragraph_count += 1

        if normalized in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            for candidate in self._candidate_stack:
                candidate.heading_count += 1

        if normalized == "li":
            for candidate in self._candidate_stack:
                candidate.list_item_count += 1

        if normalized in _BLOCK_TAGS:
            self._append_boundary()

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()

        if normalized in _IGNORED_TAGS:
            if self._ignored_depth > 0:
                self._ignored_depth -= 1
            return

        if self._ignored_depth > 0:
            return

        if normalized in _BLOCK_TAGS:
            self._append_boundary()

        if normalized in _CONTAINER_TAGS and self._candidate_stack:
            candidate = self._candidate_stack.pop()
            self._completed_candidates.append(candidate)

        if normalized == "a" and self._link_depth > 0:
            self._link_depth -= 1

        if normalized == "body" and self._body_depth > 0:
            self._body_depth -= 1

    def handle_startendtag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        del attrs

        if self._ignored_depth > 0:
            return

        if tag.lower() in _BLOCK_TAGS:
            self._append_boundary()

    def handle_data(self, data: str) -> None:
        if self._ignored_depth > 0:
            return

        cleaned = " ".join(data.split())

        if not cleaned:
            return

        inside_link = self._link_depth > 0

        for candidate in self._candidate_stack:
            candidate.add_text(
                cleaned,
                inside_link=inside_link,
            )

        if self._body_depth > 0:
            self._fallback_parts.append(cleaned)

    def _append_boundary(self) -> None:
        for candidate in self._candidate_stack:
            candidate.add_boundary()

        if self._body_depth > 0:
            self._fallback_parts.append("\n")

    @staticmethod
    def _render_parts(parts: list[str]) -> str:
        lines: list[str] = []
        current_line: list[str] = []

        def flush_line() -> None:
            if not current_line:
                return

            line = " ".join(current_line).strip()
            current_line.clear()

            if line:
                lines.append(line)

        for part in parts:
            if part == "\n":
                flush_line()
                continue

            current_line.append(part)

        flush_line()
        return "\n".join(lines).strip()

    def text(self) -> str:
        # Semantic containers are authoritative whenever they contain
        # non-empty text. They intentionally bypass the minimum density
        # threshold because a valid <article> or <main> can be short.
        article_candidates = [
            candidate
            for candidate in self._completed_candidates
            if candidate.tag == "article"
            and candidate.rendered_text()
        ]
        if article_candidates:
            best_article = max(
                article_candidates,
                key=lambda candidate: (
                    len(candidate.rendered_text()),
                    candidate.paragraph_count,
                    candidate.heading_count,
                ),
            )
            return best_article.rendered_text()

        main_candidates = [
            candidate
            for candidate in self._completed_candidates
            if candidate.tag == "main"
            and candidate.rendered_text()
        ]
        if main_candidates:
            best_main = max(
                main_candidates,
                key=lambda candidate: (
                    len(candidate.rendered_text()),
                    candidate.paragraph_count,
                    candidate.heading_count,
                ),
            )
            return best_main.rendered_text()

        # Density scoring is only needed when semantic containers are absent.
        density_candidates = [
            candidate
            for candidate in self._completed_candidates
            if candidate.tag in {"section", "div"}
            and candidate.score() != float("-inf")
        ]
        if density_candidates:
            best = max(
                density_candidates,
                key=lambda candidate: candidate.score(),
            )
            best_text = best.rendered_text()
            if best_text:
                return best_text

        return self._render_parts(self._fallback_parts)


def _validate_public_url(url: str) -> None:
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Web reader only supports http and https URLs.")

    if not parsed.hostname:
        raise ValueError("Web reader requires a URL with a hostname.")

    hostname = parsed.hostname.lower()

    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise ValueError("Web reader rejects localhost URLs.")

    try:
        addresses = socket.getaddrinfo(
            hostname,
            parsed.port or (443 if parsed.scheme == "https" else 80),
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as error:
        raise WebToolError(
            "Web reader could not resolve the target hostname."
        ) from error

    if not addresses:
        raise WebToolError(
            "Web reader could not resolve the target hostname."
        )

    for address_info in addresses:
        ip_text = address_info[4][0]

        try:
            ip = ipaddress.ip_address(ip_text)
        except ValueError as error:
            raise WebToolError(
                "Web reader resolved an invalid IP address."
            ) from error

        if not ip.is_global:
            raise ValueError(
                "Web reader rejects non-public network targets."
            )


def _content_type_is_allowed(content_type: str) -> bool:
    normalized = content_type.lower().split(";", 1)[0].strip()

    return any(
        normalized.startswith(prefix)
        for prefix in _ALLOWED_CONTENT_TYPES
    )


def _decode_content(
    raw_content: bytes,
    content_type: str,
    encoding: str | None,
) -> str:
    charset = encoding or "utf-8"
    text = raw_content.decode(charset, errors="replace")

    if "html" not in content_type.lower():
        return text.strip()

    parser = _ContentDensityExtractor()
    parser.feed(text)
    parser.close()

    return parser.text().strip()


def http_reader(
    url: str,
    *,
    timeout_seconds: float = WEB_READ_TIMEOUT_SECONDS,
    max_bytes: int = WEB_READ_MAX_BYTES,
    client: httpx.Client | None = None,
) -> str:
    if max_bytes <= 0:
        raise ValueError("max_bytes must be greater than zero.")

    owns_client = client is None
    http_client = client or httpx.Client(
        timeout=timeout_seconds,
        follow_redirects=False,
        headers={
            "User-Agent": (
                "linkedin-agentic-ai-system/0.1 "
                "(bounded research reader)"
            )
        },
    )

    current_url = url

    try:
        for redirect_count in range(_MAX_REDIRECTS + 1):
            _validate_public_url(current_url)

            with http_client.stream("GET", current_url) as response:
                if response.status_code in _REDIRECT_STATUS_CODES:
                    location = response.headers.get("location")

                    if not location:
                        raise WebToolError(
                            "Web reader received a redirect without "
                            "a Location header."
                        )

                    if redirect_count >= _MAX_REDIRECTS:
                        raise WebToolError(
                            "Web reader exceeded the redirect limit."
                        )

                    current_url = urljoin(
                        str(response.request.url),
                        location,
                    )
                    continue

                response.raise_for_status()

                content_type = response.headers.get(
                    "content-type",
                    "application/octet-stream",
                )

                if not _content_type_is_allowed(content_type):
                    raise WebToolError(
                        "Web reader rejected a non-text response."
                    )

                chunks: list[bytes] = []
                total_bytes = 0

                for chunk in response.iter_bytes():
                    total_bytes += len(chunk)

                    if total_bytes > max_bytes:
                        raise WebToolError(
                            "Web reader response exceeded the configured "
                            "content-size limit."
                        )

                    chunks.append(chunk)

                content = b"".join(chunks)

                return _decode_content(
                    raw_content=content,
                    content_type=content_type,
                    encoding=response.encoding,
                )

        raise WebToolError(
            "Web reader exceeded the redirect limit."
        )

    except httpx.TimeoutException as error:
        raise WebToolError(
            "Web reader request timed out."
        ) from error

    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        raise WebToolError(
            f"Web reader returned HTTP {status_code}."
        ) from error

    except httpx.HTTPError as error:
        raise WebToolError(
            "Web reader request failed."
        ) from error

    finally:
        if owns_client:
            http_client.close()
