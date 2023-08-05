
import buildutils.command.publish as publish

def test_parseurl():
    tests = [('scp://user@host/full/path',
              ('scp', 'user', None, 'host', None, '/full/path'))]
    for url, expected in tests:
        actual = publish.parseurl(url)
        assert actual == expected
    
