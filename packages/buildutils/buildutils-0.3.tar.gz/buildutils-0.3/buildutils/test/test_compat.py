"""Unit tests for the buildutils.compat package."""

def test_string_template():
    from buildutils.compat.string_template import Template
    actual = Template('hello ${who}').substitute({'who':'world'})
    expected = 'hello world'
    assert actual == expected
