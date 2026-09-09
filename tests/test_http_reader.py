import socket
from unittest.mock import patch

import httpx
import pytest

from app.tools.errors import WebToolError
from app.tools.http_reader import http_reader


PUBLIC_DNS_RESULT = [
    (
        socket.AF_INET,
        socket.SOCK_STREAM,
        6,
        "",
        ("93.184.216.34", 443),
    )
]


def test_http_reader_reads_and_extracts_html_text():
    html = """
    <html>
        <head>
            <style>body { color: red; }</style>
        </head>
        <body>
            <h1>Agentic AI</h1>
            <p>Useful supply chain evidence.</p>
            <script>alert("ignore");</script>
        </body>
    </html>
    """

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/html; charset=utf-8"},
            text=html,
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler)
    )

    try:
        with patch(
            "app.tools.http_reader.socket.getaddrinfo",
            return_value=PUBLIC_DNS_RESULT,
        ):
            content = http_reader(
                "https://example.com/article",
                client=client,
            )
    finally:
        client.close()

    assert "Agentic AI" in content
    assert "Useful supply chain evidence." in content
    assert "color: red" not in content
    assert 'alert("ignore")' not in content


def test_http_reader_rejects_non_http_scheme():
    with pytest.raises(
        ValueError,
        match="only supports http and https",
    ):
        http_reader("file:///etc/passwd")


def test_http_reader_rejects_private_network_target():
    private_dns_result = [
        (
            socket.AF_INET,
            socket.SOCK_STREAM,
            6,
            "",
            ("127.0.0.1", 80),
        )
    ]

    with patch(
        "app.tools.http_reader.socket.getaddrinfo",
        return_value=private_dns_result,
    ):
        with pytest.raises(
            ValueError,
            match="non-public network targets",
        ):
            http_reader("http://internal.example/resource")


def test_http_reader_rejects_non_text_content():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/pdf"},
            content=b"%PDF-test",
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler)
    )

    try:
        with patch(
            "app.tools.http_reader.socket.getaddrinfo",
            return_value=PUBLIC_DNS_RESULT,
        ):
            with pytest.raises(
                WebToolError,
                match="non-text response",
            ):
                http_reader(
                    "https://example.com/report.pdf",
                    client=client,
                )
    finally:
        client.close()


def test_http_reader_enforces_content_size_limit():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/plain"},
            content=b"x" * 20,
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler)
    )

    try:
        with patch(
            "app.tools.http_reader.socket.getaddrinfo",
            return_value=PUBLIC_DNS_RESULT,
        ):
            with pytest.raises(
                WebToolError,
                match="content-size limit",
            ):
                http_reader(
                    "https://example.com/large",
                    max_bytes=10,
                    client=client,
                )
    finally:
        client.close()


def test_http_reader_revalidates_redirect_targets():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            302,
            headers={"location": "http://private.example/secret"},
        )

    public_then_private = [
        PUBLIC_DNS_RESULT,
        [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                ("127.0.0.1", 80),
            )
        ],
    ]

    client = httpx.Client(
        transport=httpx.MockTransport(handler)
    )

    try:
        with patch(
            "app.tools.http_reader.socket.getaddrinfo",
            side_effect=public_then_private,
        ):
            with pytest.raises(
                ValueError,
                match="non-public network targets",
            ):
                http_reader(
                    "https://example.com/start",
                    client=client,
                )
    finally:
        client.close()
