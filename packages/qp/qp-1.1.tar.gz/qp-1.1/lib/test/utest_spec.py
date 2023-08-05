"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/lib/test/utest_spec.py $
$Id: utest_spec.py 27645 2005-10-30 23:46:31Z dbinger $
"""
from durus.persistent import Persistent
from qp.lib.spec import ascii, sequence, eq, anything, mapping, equal, string
from qp.lib.spec import both, length, no, boolean, get_spec, get_spec_report
from qp.lib.spec import get_spec_problems, match, require, format_spec
from qp.lib.spec import interval, subclass, instance, ascii, charset, pattern
from qp.lib.spec import spec, nspec, either, get_spec_doc, get_specs, specify
from qp.lib.spec import identifier_pattern, with_attribute
from sancho.utest import UTest, raises

class SpecTest (UTest):

    def check_match (self):
        assert match(1, int)
        assert not match(2.5, int)
        assert match(2.5, either(int, float))
        assert not match('s', either(int, float))
        assert not match('hello', sequence(int, str))
        assert match('hello', sequence(str, str))
        assert not match('hello', sequence(str, tuple))
        assert match('hello', str)
        assert match('hello', either('yes', 'no', 'hello', int))
        assert match(3, either('yes', 'no', 'hello', int))
        mydict = {'a': 1, 'b': None}
        assert match(mydict, dict)
        assert match(mydict, { str : object })
        assert not match(mydict, { int : object })
        assert match(mydict, { str : object, int : object })
        assert match((2,3), (int, int))
        assert match((1,), tuple)
        assert match((1,), sequence(object, tuple))
        assert match((1,2,3,4), sequence(object, tuple))
        assert match((1,2,3,'ok'), sequence(object, tuple))
        assert not match((1,2,3,'ok'), sequence(int, tuple))
        assert match(mydict, mapping({ either(str, int) : object }))
        assert not match(mydict, mapping({int:object}, dict))
        assert not match(mydict, mapping({str: int}))
        assert match(True, boolean)
        assert not match(3, boolean)
        assert match([3,'ok'], [int, str])
        assert not match([3,'ok', 3], [int, str])
        assert match(3, no(None))
        assert match([3, 4], [both(int, no(None))])
        assert not match(3, either)
        assert match(3, object)
        a=[2,3]
        b=[2,3]
        assert match(a, eq(a))
        assert not match(b, eq(a))
        assert match(a, equal(b))
        assert match('a', ascii)
        assert not match('\x99', ascii)
        assert not match(unicode('\x99', 'latin1'), ascii)
        assert match('a', string)
        assert not match('\x99', string)
        assert match(unicode('\x99', 'latin1'), string)
        assert match('a', length(1))
        assert match('a', interval('a','c'))
        assert not match('b', both(length(2)))
        assert match(10, interval(1))
        assert match(1, interval(1))
        assert not match(0, interval(1))
        assert not match(0, interval(1,4))
        assert match(4, interval(1,4))
        assert not match(5, interval(1,4))
        assert match(0, interval(anything,4))
        assert match(0, instance('int'))
        assert not match(0, no(int))

        class foo (dict, UTest):
            pass
        assert not match(0, subclass(dict))
        assert match(foo, subclass(dict))
        assert not match(0, mapping())
        assert not match(0, mapping({int:int},foo))
        sequence().get_args()
        assert not match(0, instance('foo'))
        for s in ('equal(1)',
                  'eq(1)',
                  'ascii',
                  'sequence(2, anything)',
                  'interval(2, 4)',
                  'interval(2)',
                  'interval()',
                  'interval(anything, 3)',
                  'None',
                  'string',
                  '(int, str)',
                  '[int]',
                  '{int: str}',
                  "'constant'",
                  ):
            assert format_spec(eval(s)) == s
        raises(TypeError, require, 1, str)
        raises(TypeError, require, 1, str, 'oops')
        assert not match(1, [1])
        assert not match([1], [str])
        assert not match([1, 'hello'], [str, str])
        assert not match(1, {})
        class mytest:
            def __call__ (self, value):
                return True
        assert match(1, mytest())

    def check_specified (self):
        class A:
            flavor_is = spec(either('sweet', 'sour'), 'the flavor')
            texture_is = spec(int, 'roughness')

        class B(A):
            color_is = spec(str)
            texture_is = nspec(str)

        self.a = A()
        self.b = B()
        self.b.color = self.b.texture = 'ok'
        specify(self.b, flavor='sweet')
        assert get_spec_problems(self.b) == []
        self.b.nonsense = 34
        assert len(get_spec_problems(self.b)) == 1
        del self.b.nonsense
        assert len(get_spec_problems(self.b)) == 0
        self.b.color = 42
        assert len(get_spec_problems(self.b)) == 1
        self.b.color = 'red'
        assert len(get_spec_problems(self.b)) == 0
        assert len(get_specs(B).values()) == 3
        def is_texture(value):
            return value in (3,4)
        class C(Persistent):
            color_is = nspec(str, 'the color')
            texture_is = is_texture
        assert get_specs(C)
        assert get_spec_doc(C)
        nspec(None)
        nspec(int)
        nspec(either(int, str))
        get_spec(C, 'texture_is')
        class D:
            color_is = nspec(str, 'the color')
            texture_is = is_texture
        get_spec(D, 'texture_is')
        get_spec_problems(D())
        class E:
            pass
        get_spec_report([D()])
        get_spec_report([E()])
        get_spec_report([])

    def check_specify (self):
        class A:
            flavor_is = spec(either('sweet', 'sour'), 'the flavor')
            texture_is = spec(int, 'roughness')

        class B(A):
            color_is = spec(str)
            texture_is = nspec(str)
        b = B()
        specify(b, texture='ok', flavor='sour')
        c = B()
        raises(TypeError, specify, c, texture=1)
        raises(AttributeError, specify, c, boo=1)

    def check_strings(self):
        assert pattern('.$')('a')
        assert not pattern('.$')('ab')
        assert str(pattern('.$')) == "pattern('.$')"
        assert pattern('.+@.+')('foo@bar')
        assert not pattern('.+@.+')('@bar')
        assert ascii('as')
        assert ascii(u'as')
        assert not ascii(u'as\u2019')
        assert not ascii('\xff')
        assert not charset('utf16')('\x33')
        assert identifier_pattern('utf_16')
        assert not identifier_pattern('8tf16')
        assert not identifier_pattern('8t-f16')
        assert match("a", u"a")
        assert not match("a\x99", u"aa")
        
    def check_with_attribute(self):
        self.a = 1
        self.b = 's'
        assert with_attribute(a=int, b=str)(self)
        assert not with_attribute(x=int)(self)
        assert str(with_attribute(a=int, b=str)) == (
            "with_attribute(a=int, b=str)")

if __name__ == "__main__":
    SpecTest()
