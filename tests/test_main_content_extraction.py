from app.tools.http_reader import _decode_content


def decode_html(html: str) -> str:
    return _decode_content(
        raw_content=html.encode("utf-8"),
        content_type="text/html; charset=utf-8",
        encoding="utf-8",
    )


def test_article_is_preferred_over_navigation_and_other_page_content():
    html = """
    <html>
        <body>
            <nav>Products Services Careers</nav>
            <div>Promotional banner outside article.</div>
            <article>
                <h1>Agentic AI transforms supply chains</h1>
                <p>First useful paragraph.</p>
                <p>Second useful paragraph.</p>
            </article>
            <footer>Privacy Cookies Contact</footer>
        </body>
    </html>
    """

    content = decode_html(html)

    assert "Agentic AI transforms supply chains" in content
    assert "First useful paragraph." in content
    assert "Second useful paragraph." in content
    assert "Products Services Careers" not in content
    assert "Promotional banner outside article." not in content
    assert "Privacy Cookies Contact" not in content


def test_main_is_used_when_page_has_no_article():
    html = """
    <html>
        <body>
            <header>Site header</header>
            <nav>Navigation</nav>
            <main>
                <h1>Research report</h1>
                <p>Useful main content.</p>
            </main>
            <div>Recommended stories outside main.</div>
            <footer>Footer links</footer>
        </body>
    </html>
    """

    content = decode_html(html)

    assert "Research report" in content
    assert "Useful main content." in content
    assert "Site header" not in content
    assert "Navigation" not in content
    assert "Recommended stories outside main." not in content
    assert "Footer links" not in content


def test_article_ignores_nested_boilerplate_containers():
    html = """
    <html>
        <body>
            <article>
                <h1>Useful title</h1>
                <aside>Related content that should not be included.</aside>
                <p>Useful evidence.</p>
                <form>Newsletter signup</form>
                <footer>Article footer boilerplate</footer>
            </article>
        </body>
    </html>
    """

    content = decode_html(html)

    assert "Useful title" in content
    assert "Useful evidence." in content
    assert "Related content" not in content
    assert "Newsletter signup" not in content
    assert "Article footer boilerplate" not in content


def test_body_fallback_preserves_visible_content_without_article_or_main():
    html = """
    <html>
        <head>
            <title>Metadata title</title>
            <style>.hidden { display: none; }</style>
        </head>
        <body>
            <nav>Navigation</nav>
            <div>
                <h1>Legacy page title</h1>
                <p>Useful content on an older page.</p>
            </div>
            <script>alert("ignore");</script>
            <footer>Footer</footer>
        </body>
    </html>
    """

    content = decode_html(html)

    assert "Legacy page title" in content
    assert "Useful content on an older page." in content
    assert "Metadata title" not in content
    assert "Navigation" not in content
    assert "alert" not in content
    assert "Footer" not in content


def test_non_html_text_is_left_unchanged():
    content = _decode_content(
        raw_content=b"Plain text research evidence.\nSecond line.",
        content_type="text/plain; charset=utf-8",
        encoding="utf-8",
    )

    assert content == "Plain text research evidence.\nSecond line."
    