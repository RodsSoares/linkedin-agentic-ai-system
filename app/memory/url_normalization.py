from urllib.parse import (
    parse_qsl,
    urlencode,
    urlsplit,
    urlunsplit,
)


TRACKING_QUERY_PARAMETERS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_id",
    "fbclid",
    "gclid",
    "dclid",
    "msclkid",
}


def canonicalize_url(url: str) -> str:
    """
    Convert a URL into a stable representation suitable for persistent
    deduplication.

    v0.1 rules:
    - accept only http/https URLs;
    - lowercase scheme and host;
    - remove fragments;
    - remove known tracking query parameters;
    - preserve potentially functional query parameters;
    - sort remaining query parameters deterministically;
    - remove default ports;
    - remove non-root trailing slash.

    This function intentionally avoids aggressive URL rewriting because
    query parameters may identify genuinely different content.
    """

    if not isinstance(url, str):
        raise TypeError("url must be a string")

    url = url.strip()

    if not url:
        raise ValueError("url must not be empty")

    parsed = urlsplit(url)

    scheme = parsed.scheme.lower()

    if scheme not in {"http", "https"}:
        raise ValueError("url must use http or https")

    hostname = parsed.hostname

    if not hostname:
        raise ValueError("url must contain a hostname")

    hostname = hostname.lower()

    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("url contains an invalid port") from exc

    if port is None:
        netloc = hostname
    elif scheme == "http" and port == 80:
        netloc = hostname
    elif scheme == "https" and port == 443:
        netloc = hostname
    else:
        netloc = f"{hostname}:{port}"

    if parsed.username or parsed.password:
        raise ValueError("urls containing credentials are not supported")

    path = parsed.path or "/"

    if path != "/":
        path = path.rstrip("/")

        if not path:
            path = "/"

    filtered_query_items = [
        (key, value)
        for key, value in parse_qsl(
            parsed.query,
            keep_blank_values=True,
        )
        if key.lower() not in TRACKING_QUERY_PARAMETERS
    ]

    filtered_query_items.sort()

    query = urlencode(filtered_query_items, doseq=True)

    return urlunsplit(
        (
            scheme,
            netloc,
            path,
            query,
            "",
        )
    )
