from cosrlib.document.html import HTMLDocument
import pytest


def _links(html, url=None):
    return HTMLDocument(html, url=url).parse().get_hyperlinks()


def test_get_hyperlinks():
    links = _links("""<html><head><title>Test title</title></head><body>x</body></html>""")
    assert len(links) == 0

    links = _links("""<html><head><title>Test title</title></head><body>
        <a name="x">Y</a>
    </body></html>""")
    assert len(links) == 0

    links = _links("""<html><head><title>Test title</title></head><body>
        <a href="">Y</a>
    </body></html>""")
    assert len(links) == 0

    links = _links("""<html><head><title>Test title</title></head><body>
        <a href="ftp://test.com">Y</a>
    </body></html>""")
    assert len(links) == 0

    links = _links("""<html><head><title>Test title</title></head><body>
        <a href="http://sub.test.com/page1?q=2&a=b#xxx">Y</a>
    </body></html>""")
    assert len(links) == 1
    assert links[0]["href"].url == "http://sub.test.com/page1?q=2&a=b#xxx"
    assert links[0]["words"] == ["Y"]

    links = _links("""<html><head><title>Test title</title></head><body>
        <a href="/page1?q=2&a=b#xxx">Y</a>
    </body></html>""", url="http://sub.test.com/page2")
    assert len(links) == 1
    assert links[0]["href"].url == "http://sub.test.com/page1?q=2&a=b#xxx"
    assert links[0]["words"] == ["Y"]

    links = _links("""<html><head><title>Test title</title></head><body>
        <a href="../page1?q=2&a=b#xxx">Y</a>
    </body></html>""", url="http://sub.test.com/page2/x.html")
    assert len(links) == 1
    assert links[0]["href"].url == "http://sub.test.com/page1?q=2&a=b#xxx"
    assert links[0]["words"] == ["Y"]

    links = _links("""<html><head><title>Test title</title></head><body>
        <a href="http://UPPER.CASE.coM/PATH?QUERY=V">Y</a>
    </body></html>""", url="http://sub.test.com/page2/x.html")
    assert len(links) == 1
    assert links[0]["href"].url == "http://upper.case.com/PATH?QUERY=V"
    assert links[0]["words"] == ["Y"]

    links = _links("""<html><head><title>Test title</title></head><body>
        <a href="//UPPER.CASE.coM/PATH?QUERY=V">Y</a>
    </body></html>""", url="http://sub.test.com/page2/x.html")
    assert len(links) == 1
    assert links[0]["href"].url == "http://upper.case.com/PATH?QUERY=V"
    assert links[0]["words"] == ["Y"]

    # We do not index links behind any kind of auth
    links = _links("""<html><head><title>Test title</title></head><body>
        <a href="http://user@domain.com">Y</a>
    </body></html>""", url="http://sub.test.com/page2/x.html")
    assert len(links) == 0

    # Looks like a forgotten mailto:, don't index
    links = _links("""<html><head><title>Test title</title></head><body>
        <a href="user@domain.com">Y</a>
    </body></html>""", url="http://sub.test.com/page2/x.html")
    assert len(links) == 0

    # Invalid URL should be filtered
    links = _links("""<html><head><title>Test title</title></head><body>
        <a href="http://www.[wsj-ticker ticker=">Y</a>
    </body></html>""", url="http://sub.test.com/page2/x.html")
    assert len(links) == 0

    links = _links("""<html><head><title>Test title</title></head><body>
        <a href="<object width=">Y</a>
    </body></html>""", url="http://sub.test.com/page2/x.html")
    assert len(links) == 0

    links = _links("""<html><head><title>Test title</title></head><body>
        <a href="http://<object width=">Y</a>
    </body></html>""", url="http://sub.test.com/page2/x.html")
    assert len(links) == 0

    # We don't index TLDs either
    links = _links("""<html><head><title>Test title</title></head><body>
        <a href="http://com/x">Y</a>
    </body></html>""", url="http://sub.test.com/page2/x.html")
    assert len(links) == 0

    links = _links("""<html><head><title>Test title</title></head><body>
        <a href="http://newunknowntldxx/x">Y</a>
    </body></html>""", url="http://sub.test.com/page2/x.html")
    assert len(links) == 0


def test_get_hyperlinks_base_tag():

    links = _links("""<html><head><base href="https://example.com/d1/d2/" /><title>Test title</title></head><body>
        <a href="../page1?q=2&a=b#xxx">Y</a>
    </body></html>""", url="http://sub.test.com/page2/x.html")
    assert len(links) == 1
    assert links[0]["href"].url == "https://example.com/d1/page1?q=2&a=b#xxx"
    assert links[0]["words"] == ["Y"]


def test_get_hyperlinks_no_follow_meta_tag():

    links = _links("""<html><head><META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW">
                </head><body>
                before
                <a href="http://example.com/page1">link text</a>
                after

                <a href="/page2">relative2</a>
                <a href="page3?q=1#d">relative3</a>
                <a href="http://other.example.com/page4">absolute4</a>
                <a href="//other.example.com/page5?q=1#d">absolute5</a>
                <a href="https://other.example.com/page6?q=1#d">absolute6</a>
                <a href="javascript:func()">js1</a>

                </body></html>""")

    # No links returned for document with nofollow in robots meta tag
    assert len(links) == 0


def test_get_hyperlinks_no_follow_http_header():

    doc = HTMLDocument("""<html><head></head><body>
                before
                <a href="http://example.com/page1">link text</a>
                after

                <a href="/page2">relative2</a>
                <a href="page3?q=1#d">relative3</a>
                <a href="http://other.example.com/page4">absolute4</a>
                <a href="//other.example.com/page5?q=1#d">absolute5</a>
                <a href="https://other.example.com/page6?q=1#d">absolute6</a>
                <a href="javascript:func()">js1</a>

                </body></html>""",
                       headers={'X-Robots-Tag': 'NoIndex, NoFollow'}).parse()
    links = doc.get_hyperlinks()

    # No links returned for document with nofollow in the robots http header
    assert len(links) == 0
