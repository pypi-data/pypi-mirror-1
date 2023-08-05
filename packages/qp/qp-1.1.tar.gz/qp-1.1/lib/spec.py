"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/lib/spec.py $
$Id: spec.py 27645 2005-10-30 23:46:31Z dbinger $

This module provides tools for matching values to specs.

In particular, it provides the functions
  match(),
  require()

This module also provides tools for constructing specs,
using them to specify and validate instance attributes.
"""

import re
from types import FunctionType, MethodType

def format_spec(spec):
    """
    Returns the canonical string representation of the spec.
    """
    if spec is None:
        return 'None'
    if type(spec) is tuple:
        return '(%s)' % ', '.join(map(format_spec, spec))
    if type(spec) is list:
        return '[%s]' % ', '.join(map(format_spec, spec))
    if type(spec) is dict:
        return ('{%s}' %
                ', '.join(["%s: %s" % (format_spec(key_type),
                                       format_spec(val_type)) #nocover
                           for key_type, val_type in spec.items()]))
    if hasattr(spec, '__name__'):
        return spec.__name__
    if isinstance(spec, basestring):
        return repr(spec)
    return str(spec)

class SpecOperator:
    """
    The superclass of all of the spec operators.
    Constructors of subclasses should assign to self.args
    a tuple of the arguments to the constructor.
    """

    def get_args(self):
        return self.args

    def format_args(self):
        return ', '.join(map(format_spec, self.get_args()))

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self.format_args())

def match(value, spec):
    """
    Return True or False depending on whether or not value matches
    the given type specification.  Here are the available type
    specifications:

    Type Spec                Matches

    a type or class         any instance of the type

    a callable              anything for which <spec>(value) is true,
                            so you can do arbitrary checking.

    a list (or tuple)       any list (tuple) whose elements all match the
    with length 1           enclosed type specification.

    a list (or tuple)       any list (tuple) whose sequence of elements match
    with length > 1,        the sequence of corresponding type specifications,
    not containing None,
    or any string or numeric
    literal.

    a tuple with            any value that matches any of the items in the tuple.
    length > 1
    containing None,
    or any string or
    numeric
    literal.

    a dict                  any dict for which every item matches some item in
                            this dictionary.

    other                   any value for which value == other.

    """
    if isinstance(spec, (FunctionType, SpecOperator, Specification)):
        return spec(value)
    spec_type = type(spec)
    if spec_type is tuple and len(spec) > 1:
        # Possible disjunction.
        for element in spec:
            if (element is None or
                type(element) in (float, int, str, unicode)):
                # Definite disjunction.
                for element in spec:
                    if match(value, element):
                        return True
                return False
    if spec_type in (list, tuple):
        if type(value) is not spec_type:
            return False
        if len(spec) == 1:
            element_type = spec[0]
            for element in value:
                if not match(element, element_type):
                    return False
            return True
        else:
            if len(value) != len(spec):
                return False
            for element, element_type in zip(value, spec):
                if not match(element, element_type):
                    return False
            return True
    if spec_type is dict:
        if type(value) is not dict:
            return False
        for key, val in value.items():
            for key_type, value_type in spec.items():
                if (match(key, key_type) and
                    match(val, value_type)):
                    break
            else:
                return False
        return True
    try:
        return isinstance(value, spec)
    except TypeError:
        pass
    if spec_type is type(value):
        return value == spec
    if callable(spec):
        return spec(value)
    try:
        return value == spec
    except (TypeError, ValueError, AssertionError):
        pass
    return False

def require(value, spec, message=None):
    if not match(value, spec):
        error = ('\n  Expected: %s\n'
                 '  Got: %r\n') % (format_spec(spec), value)
        if message:
            error = '(%s)%s' % (message, error)
        raise TypeError(error)

def anything(value):
    """
    The universal spec.
    """
    return True


class sequence (SpecOperator):

    """
    Use this to specify a sequence.
    """

    def __init__(self, element_spec=anything, container_spec=anything):
        self.container_spec = container_spec
        self.element_spec = element_spec
        self.args = (element_spec, container_spec)

    def __call__(self, value):
        if not match(value, self.container_spec):
            return False
        element_spec = self.element_spec
        for element in value:
            if not match(element, element_spec):
                return False
        return True


class mapping (SpecOperator):

    """
    Use this to specify a mapping.
    """

    def __init__(self, dict_spec=anything, container_spec=anything):
        self.dict_spec = dict_spec
        self.container_spec = container_spec
        self.args =  (self.dict_spec, container_spec)

    def __call__(self, value):
        if not match(value, self.container_spec):
            return False
        try:
            dict_value = dict(value.items())
        except AttributeError:
            return False
        if not match(dict_value, self.dict_spec):
            return False
        return True

class subclass (SpecOperator):

    """
    Use this to specify a subclass of a given class.
    """

    def __init__(self, klass):
        self.klass = klass
        self.args = (klass,)

    def __call__(self, value):
        try:
            return issubclass(value, self.klass)
        except TypeError:
            return False


class instance (SpecOperator):

    """
    Use this to specify an instance of a class with a given name
    when the class itself is not available.
    """

    def __init__(self, klass_name):
        self.klass_name = klass_name
        self.args = (klass_name,)

    def __call__(self, value):
        if hasattr(value, '__class__'):
            classes = [value.__class__]
            while classes:
                if classes[0].__name__ == self.klass_name:
                    return True
                classes = classes[1:] + list(classes[0].__bases__)
        return False


class ConnectiveSpecOperator (SpecOperator):

    def __init__(self, *specs):
        self.specs = specs
        self.args = self.specs


class no (ConnectiveSpecOperator):

    """
    Use this to specify a negation of specs.
    Example: no(None)
    """

    def __call__(self, value):
        for spec in self.specs:
            if match(value, spec):
                return False
        return True


class both (ConnectiveSpecOperator):

    """
    Use this to specify a conjunction of specs.
    Example:
      both([int], length(3)) specifies values that are lists of 3 ints.
    """

    def __call__(self, value):
        for spec in self.specs:
            if not match(value, spec):
                return False
        return True


class either (ConnectiveSpecOperator):

    """
    Use this to specify a disjunction of specs.
    Examples:
      either(int, str) specifies values that are ints or strs.
    """

    def __call__(self, value):
        for spec in self.specs:
            if match(value, spec):
                return True
        return False


class interval (SpecOperator):

    def __init__(self, min=anything, max=anything):
        self.min = min
        self.max = max

    def format_args(self):
        if self.max is anything:
            if self.min is anything:
                return ''
            return format_spec(self.min)
        else:
            return '%s, %s' % (format_spec(self.min), format_spec(self.max))

    def __call__(self, value):
        if self.min not  in (None, anything):
            if self.max is anything:
                return value >= self.min
            elif value < self.min:
                return False
        if self.max not  in (None, anything):
            if self.min is anything:
                return value <= self.max
            elif value > self.max:
                return False
        return True


class length (interval):

    """
    Use this to specify specs by ranges of length.
    Examples:
      length(3, None) specifies values of length 3 or more.
      length(3) specifies values of length 3.
    """

    def __call__(self, value):
        return interval.__call__(self, len(value))


class eq (SpecOperator):

    """
    Use this to specify specs exact value.
    Examples:
      eq(SpecOperator) matches the SpecOperator class, but nothing else.

    """

    def __init__(self, value):
        self.value = value

    def format_args(self):
        return repr(self.value)

    def __call__(self, value):
        return value is self.value


class equal (SpecOperator):

    """
    Use this to specify specs exact value.
    Examples:
      eq([2,3]) matches any list [2,3]

    """

    def __init__(self, value):
        self.value = value

    def format_args(self):
        return repr(self.value)

    def __call__(self, value):
        return value == self.value

boolean = either(True, False, 0, 1)


class charset (SpecOperator):

    def __init__(self, charset):
        self.charset = charset

    def __str__(self):
        return self.charset

    def __call__(self, value):
        if isinstance(value, unicode):
            try:
                value.encode(self.charset)
            except UnicodeEncodeError:
                return False
        elif isinstance(value, str):
            try:
                unicode(value, self.charset)
            except UnicodeDecodeError:
                return False
        else:
            return False
        return True


ascii = charset('ascii')


class String (SpecOperator):

    """
    This is the common string class, it ascii str instances and
    all unicode instances.  
    """

    def __str__(self):
        return 'string'

    def __call__(self, value):
        if isinstance(value, unicode):
            return True
        elif isinstance(value, str):
            try:
                unicode(value, 'ascii')
                return True
            except UnicodeDecodeError:
                return False
        return False

string = String()


class pattern (SpecOperator):
    """
    Matches basestrings that match the regular expression.
    """
    def __init__(self, pattern):
        self.pattern = re.compile(pattern)
        self.args = (pattern,)

    def __call__(self, value):
        try:
            return bool(self.pattern.match(value))
        except TypeError:
            return False

identifier_pattern = pattern('[a-zA-Z_][a-zA-Z0-9_]*$')

class with_attribute (SpecOperator):
    """
    Matches values with attributes matching given specs.
    A keyword argument gives the spec for each attribute.
    """    
    def __init__(self, **attribute_specs):
        self.attribute_specs = attribute_specs
        
    def __call__(self, value):
        for attribute, spec in self.attribute_specs.items():
            if (not hasattr(value, attribute) or 
                not match(getattr(value, attribute), spec)):
                return False
        return True
        
    def format_args(self):
        return ', '.join(['%s=%s' % (name, format_spec(spec))
                          for name, spec in sorted(self.attribute_specs.items())])

class Specification:
    """
    Instance attributes:
      doc : string
      spec : anything
    """

    def __init__(self, spec, doc=''):
        self.doc = doc
        self.spec = spec

    def __call__(self, value):
        return match(value, self.spec)

    def __str__(self):
        """-> str
        Return a formatted string describing this spec and corresponding doc.
        """
        doc = '\n  '.join([line.strip()
                           for line in self.doc.split('\n')])
        if doc:
            return self.format_spec() + '\n  ' + doc
        else:
            return self.format_spec()

    def valid(self, value):
        """(value : anything) -> bool
        Does the value match this spec?
        """
        return match(value, self.spec)

    def format_spec(self):
        """() -> str
        Return a string version of the spec.
        """
        return format_spec(self.spec)

def get_spec(klass, name):
    """(klass:anything, name:str) -> anything
    """
    value = getattr(klass, name)
    # functions as specifiers must be unwrapped, since
    # assignment to class variables changes them.
    if type(value) is MethodType: # normal classes
        spec = value.im_func
    else:
        spec = value
    return spec

def spec(spec, *docs):
    """(anything, *str) -> Specification
    An alternative Specification constructor.
    """
    doc = '\n'.join(docs)
    return Specification(spec, doc)

def nspec(spec, *docs):
    """(anything, *str) -> Specification
    Like spec, but this uses a modified Specification (if needed) to make
    sure that None is a valid value.
    For applications that always want None as a valid value, this
    allows us to avoid using the either(None,*) pattern around every spec.
    """
    doc = '\n'.join(docs)
    s = Specification(spec, doc)
    if s.valid(None):
        return s
    if isinstance(spec, either):
        return Specification(either(None, *spec.get_args()), doc)
    return Specification(either(None, spec), doc)

def get_specs(klass):
    """(klass:anything) -> { str : anything }
    Returns a dictionary mapping names to specs that apply to instances of
    klass.  Specs are distinguished by the following naming convention:
    A class attribute whose name ends in '_is' specifies an instance
    attribute without the suffix.
    Example:
    class A:
        color_is = either(str, None)
        def __init__(self, x):
            self.color = x
    """
    specs = {}
    for name in dir(klass):
        if name.endswith('_is'):
            specs[name[:-3]] = get_spec(klass, name)
    return specs


def get_spec_problems(x, specs=None):
    """(x:anything, specs:{str:Spec}) -> [basestring]
    Return a list of reasons why the attributes of this
    instance do not match the specs.
    Use provided specs for speed if you already
    have the specs of the class of x.
    """
    reasons = []
    if specs is None:
        specs = get_specs(x.__class__)
    for name, spec in specs.items():
        if not hasattr(x, name):
            reasons.append(('%r.%s: Missing\n'
                            '  Expected: %s\n') % (x, name, format_spec(spec)))
        else:
            value = getattr(x, name)
            if not match(value, spec):
                reasons.append(
                    ('%r.%s:\n' #nocover
                     '  Expected: %s\n'
                     '  Got: %r\n') % ( #nocover
                    x, name, format_spec(spec), value))
    for name, value in vars(x).items():
        if not name in specs:
            reasons.append('Found non-specified attribute: %r.%s (=%r)' %
                           (x, name, value))
    return reasons

def get_spec_doc(klass):
    """(klass:Specified) -> str
    Return a string containing the docs of all specs of klass.
    """
    spec_items = get_specs(klass).items()
    spec_items.sort()
    return '\n'.join(["%s: %s" % (name, format_spec(spec))
                      for name, spec in spec_items])

def get_spec_report(instances):
    """(instances: [InstanceType]) -> str|None
    Study the instances with respect to their attribute specs.
    The instances must all be of the same class.
    If any instance does not satisfy the specs, return a
    string explaining the problem.
    If all instances satisfy the specs, return a message reporting
    the number of instances verified.
    If the class of the instances has no specifications,
    return a message that says so.
    If there are no instances, return None.
    """
    count = 0
    klass = specs = None
    for instance in instances:
        if klass is None:
            klass = instance.__class__
            specs = get_specs(klass)
            if not specs:
                return "\nunspecified " + klass.__name__
        assert instance.__class__ is klass
        count += 1
        instance_problems = get_spec_problems(instance, specs=specs)
        if instance_problems:
            return "\n%s:\n" % klass.__name__ + "\n".join(instance_problems)
    return klass and "\n%s: %s ok\n" % (klass.__name__ , count)

def specify(obj, **attributes_values):
    """(obj:object, **attributes_values:{str:anything})
    Set object attributes given as keywords.
    Raise a TypeError if any value does match a spec,
    and AttributeError if no corresponding spec is found.
    """
    for attribute, value in attributes_values.items():
        require(value, getattr(obj.__class__, attribute + '_is'))
        setattr(obj, attribute, value)

def init(obj, **attributes_values):
    """(obj:object, **attributes_values:{str:anything})
    Set object attributes given as keywords.
    Raise a TypeError if any value does match a spec,
    and AttributeError if no corresponding spec is found.
    In addition, all other specified attributes are set to None,
    without any type checking.
    """
    for name in get_specs(obj.__class__):
        if not hasattr(obj, name):
            setattr(obj, name, None)
    specify(obj, **attributes_values)

def add_getters(klass):
    """
    Add trivial getter method for each specified attribute
    for which no such method currently exists.
    """
    def add_getter(klass, name):
        accessor_name = 'get_' + name
        if not hasattr(klass, accessor_name):
            def f(self):
                return getattr(self, name)
            f.__name__ = accessor_name
            setattr(klass, accessor_name, f)
    for name in get_specs(klass):
        add_getter(klass, name)

def add_setters(klass):
    """
    Add trivial setter method for each specified attribute
    for which no such method currently exists.
    """
    def add_setter(klass, name):
        setter_name = 'set_' + name
        if not hasattr(klass, setter_name):
            def f(self, value):
                require(value, getattr(klass, name + '_is'))
                setattr(self, name, value)
            f.__name__ = setter_name
            setattr(klass, setter_name, f)
    for name in get_specs(klass):
        add_setter(klass, name)

def add_getters_and_setters(klass):
    add_getters(klass)
    add_setters(klass)



