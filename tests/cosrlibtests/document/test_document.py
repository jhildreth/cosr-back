from cosrlib.document import Document


def test_has_robots_noindex():

    doc = Document('', headers={'X-Robots-Tag': 'noindex, nofollow'})
    assert doc.has_robots_noindex() is True

    doc = Document('', headers={'X-Robots-Tag': 'NoIndex'})
    assert doc.has_robots_noindex() is True

    doc = Document('', headers={'X-Random-Header': 'noindex'})
    assert doc.has_robots_noindex() is False

    doc = Document('')
    assert doc.has_robots_noindex() is False


def test_has_robots_nofollow():

    doc = Document('', headers={'X-Robots-Tag': 'noindex, nofollow'})
    assert doc.has_robots_nofollow() is True

    doc = Document('', headers={'X-Robots-Tag': 'NoFollow'})
    assert doc.has_robots_nofollow() is True

    doc = Document('', headers={'X-Random-Header': 'nofollow'})
    assert doc.has_robots_nofollow() is False

    doc = Document('')
    assert doc.has_robots_nofollow() is False