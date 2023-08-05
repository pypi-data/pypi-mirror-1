"""pudge.rst unit tests"""

def test_rst_to_html():
    from pudge.rst import to_html
    expected = u"<p>A single <em>emphasized</em> paragraph.</p>\n"
    actual = to_html("A single *emphasized* paragraph.")
    assert actual == expected
