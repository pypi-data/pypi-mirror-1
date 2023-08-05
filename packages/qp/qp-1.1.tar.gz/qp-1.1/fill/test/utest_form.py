"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/fill/test/utest_form.py $
$Id: utest_form.py 27083 2005-07-26 18:23:56Z dbinger $
"""
from qp.fill.form import Form, get_javascript_code
from qp.fill.widget import MultipleSelectWidget
from qp.pub.common import clear_publisher
from qp.pub.hit import Hit
from qp.pub.publish import Publisher
from sancho.utest import UTest, raises

class Test(UTest):

    def _pre(self):
        clear_publisher()

    def _post(self):
        clear_publisher()

    def a(self):
        publisher = Publisher()
        hit = Hit(None, {})
        publisher.process_hit(hit)
        form = Form()
        form.add_submit('a')
        form.add_reset('b')
        form.add_hidden('c')
        form.add_string('d')
        form.add_text('e')
        form.add_checkbox('f')
        form.add_single_select('g', options=[0])
        form.add_multiple_select('h', options=[0])
        form.add_radiobuttons('i', options=[0])
        form.add_float('j')
        form.add_int('k')
        form.render()
        assert not form.is_submitted()

    def b(self):
        publisher = Publisher()
        hit = Hit(None, dict(REQUEST_METHOD="GET", QUERY_STRING='d=1'))
        publisher.process_hit(hit)
        form = Form()
        form.add_submit('a')
        form.add_string('d')
        assert not form.is_submitted()
        form.render()

    def c(self):
        publisher = Publisher()
        hit = Hit(None, dict(REQUEST_METHOD="GET", QUERY_STRING='d=1'))
        publisher.process_hit(hit)
        form = Form(method="get")
        form.add_submit('a')
        form.add_string('d')
        assert form.is_submitted()
        form.render()

    def d(self):
        publisher = Publisher()
        hit = Hit(None, dict(REQUEST_METHOD="POST"))
        publisher.process_hit(hit)
        form = Form()
        form.add_submit('a')
        form.add_string('d')
        form.set_error('a', 'err')
        assert form.is_submitted()
        form.render()

    def e(self):
        publisher = Publisher()
        hit = Hit(None, dict(REQUEST_METHOD="GET", QUERY_STRING='d=1'))
        hit.get_request().process_inputs()
        publisher.set_hit(hit)
        form = Form(method="get")
        form.add_submit('a')
        form.add_string('d')
        form.has_key('d')
        assert form.get('d') == '1'
        assert form['d'] == '1'
        assert form.is_submitted()
        get_javascript_code()['a'] = 'javascript'
        assert 'javascript' in str(form.render())

    def f(self):
        publisher = Publisher()
        hit = Hit(None, dict(REQUEST_METHOD="GET", QUERY_STRING='d=1'))
        hit.get_request().process_inputs()
        publisher.set_hit(hit)
        form = Form(method="get")
        form.add(MultipleSelectWidget, 'a', options=[range(10)])
        class FakePersistent(object): pass
        a = FakePersistent()
        b = FakePersistent()
        a._p_oid = '11111111'
        b._p_oid = '22222222'
        form.add(MultipleSelectWidget, 'b', options = [a, b])
        FakePersistent.__str__ = lambda x: 'ok'
        raises(AssertionError, # because descriptions are not unique.
               form.add, MultipleSelectWidget, 'c', options = [a, b])

if __name__ == '__main__':
    Test()
