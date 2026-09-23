from app.tools.http_reader import _decode_content


def decode_html(html: str) -> str:
    return _decode_content(
        raw_content=html.encode("utf-8"),
        content_type="text/html; charset=utf-8",
        encoding="utf-8",
    )


def test_density_extractor_prefers_editorial_block_over_large_link_menu():
    menu_links = "".join(
        f'<a href="/service/{index}">Service category number {index}</a>'
        for index in range(80)
    )

    html = f"""
    <html>
        <body>
            <div class="mega-menu">
                {menu_links}
            </div>

            <div class="article-content">
                <h1>Agentic AI transforms supply chains</h1>
                <p>
                    Agentic AI can coordinate bounded operational decisions
                    across planning, procurement and execution workflows.
                </p>
                <p>
                    The practical challenge is governance: systems need
                    explicit authority limits, evidence and human oversight.
                </p>
                <p>
                    Supply chain teams should measure execution quality,
                    exception handling and business outcomes rather than
                    conversational fluency alone.
                </p>
                <p>
                    These design choices make agentic systems more useful
                    for real operating environments.
                </p>
            </div>
        </body>
    </html>
    """

    content = decode_html(html)

    assert "Agentic AI transforms supply chains" in content
    assert "bounded operational decisions" in content
    assert "Service category number 1" not in content


def test_density_extractor_penalizes_navigation_like_list_block():
    nav_items = "".join(
        f"<li><a href='/x/{index}'>Navigation item {index}</a></li>"
        for index in range(50)
    )

    html = f"""
    <html>
        <body>
            <div class="global-menu">
                <ul>{nav_items}</ul>
            </div>

            <section class="story-body">
                <h1>Execution, not chat</h1>
                <p>
                    This article explains why agentic systems need bounded
                    autonomy and reliable operational data.
                </p>
                <p>
                    It also discusses how teams can evaluate execution
                    performance using measurable supply chain outcomes.
                </p>
                <p>
                    A strong deployment separates semantic reasoning from
                    deterministic controls.
                </p>
                <p>
                    Human approval remains important for consequential
                    external actions.
                </p>
            </section>
        </body>
    </html>
    """

    content = decode_html(html)

    assert "Execution, not chat" in content
    assert "bounded autonomy" in content
    assert "Navigation item" not in content


def test_density_extractor_keeps_article_priority():
    html = """
    <html>
        <body>
            <div class="content">
                <p>
                    A fairly long generic page introduction that is not the
                    actual editorial article and should not win.
                </p>
                <p>
                    More generic content exists here to make this block large.
                </p>
            </div>

            <article>
                <h1>Primary article</h1>
                <p>
                    This is the actual article body with useful evidence.
                </p>
                <p>
                    Another paragraph adds supporting context and detail.
                </p>
                <p>
                    A third paragraph makes the article clearly substantive.
                </p>
            </article>
        </body>
    </html>
    """

    content = decode_html(html)

    assert "Primary article" in content
    assert "actual article body" in content
    assert "generic page introduction" not in content


def test_density_extractor_ignores_nested_boilerplate():
    html = """
    <html>
        <body>
            <div class="article-body">
                <h1>Useful article title</h1>
                <p>
                    Useful paragraph about agentic supply chain execution.
                </p>
                <aside>
                    Related stories and promotional content.
                </aside>
                <p>
                    Useful paragraph about operational governance.
                </p>
                <form>
                    Newsletter signup
                </form>
                <footer>
                    Privacy and cookie links
                </footer>
                <p>
                    Useful paragraph about measurable business outcomes.
                </p>
            </div>
        </body>
    </html>
    """

    content = decode_html(html)

    assert "Useful article title" in content
    assert "operational governance" in content
    assert "measurable business outcomes" in content
    assert "Related stories" not in content
    assert "Newsletter signup" not in content
    assert "Privacy and cookie links" not in content


def test_density_extractor_falls_back_for_simple_legacy_page():
    html = """
    <html>
        <head>
            <title>Metadata title</title>
        </head>
        <body>
            <nav>Navigation</nav>
            <h1>Legacy page</h1>
            <p>Short but useful visible content.</p>
            <footer>Footer</footer>
        </body>
    </html>
    """

    content = decode_html(html)

    assert "Legacy page" in content
    assert "Short but useful visible content." in content
    assert "Metadata title" not in content
    assert "Navigation" not in content
    assert "Footer" not in content


def test_non_html_text_is_left_unchanged():
    content = _decode_content(
        raw_content=b"Plain text research evidence.\nSecond line.",
        content_type="text/plain; charset=utf-8",
        encoding="utf-8",
    )

    assert content == "Plain text research evidence.\nSecond line."
