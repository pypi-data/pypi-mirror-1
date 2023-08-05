"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/fill/test/utest_html.py $
$Id: utest_html.py 26989 2005-06-29 20:42:07Z dbinger $
"""
from sancho.utest import UTest
from qp.fill.html import href, div, ol, ul, dl, nl2br
from qpy import h8

class HTMLTest(UTest):

    def a(self):
        result = href('a', 'b', name="c")
        assert isinstance(result, h8)
        assert result == '<a href="a" name="c">b</a>'

    def b(self):
        result = div('a', 'b', c="d")
        assert isinstance(result, h8)
        assert result == '<div c="d">ab</div>'

    def c(self):
        result = ol(['a', 'b'], c="d")
        assert isinstance(result, h8)
        assert result == '<ol c="d"><li>a</li><li>b</li></ol>'

    def d(self):
        result = ul(['a', 'b'], c="d")
        assert isinstance(result, h8)
        assert result == '<ul c="d"><li>a</li><li>b</li></ul>'

    def e(self):
        result = dl([('a', 'b'), ('e', None)], c="d")
        assert isinstance(result, h8)
        assert result == '<dl c="d"><dt>a</dt><dd>b</dd><dt>e</dt></dl>'

    def f(self):
        result = nl2br('')
        assert isinstance(result, h8)
        result = nl2br('a\nb\n')
        assert isinstance(result, h8)
        assert result == 'a<br />b<br />', result

if __name__ == '__main__':
    HTMLTest()
