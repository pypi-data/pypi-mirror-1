"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/pub/common.py $
$Id: common.py 27227 2005-08-18 22:20:59Z dbinger $

Code for maintaining the global Publisher, and convenience functions
for operations that go through the publisher.
"""

_publisher = None

def set_publisher(value):
    global _publisher
    assert _publisher is None
    _publisher = value

def clear_publisher():
    # Used in test scripts only.
    global _publisher
    _publisher = None

def get_publisher():
    return _publisher

# All of the remaining functions here work through get_publisher().

def get_hit():
    return get_publisher().get_hit()

def get_request():
    return get_hit().get_request()

def get_response():
    return get_hit().get_response()

def get_session():
    return get_hit().get_session()

def get_user():
    return get_session().get_effective_user()

def get_site():
    return get_publisher().get_site()

def get_path(n=0):
    return get_request().get_path(n=n)

def redirect(location, permanent=False):
    get_publisher().redirect(location, permanent=permanent)

def not_found(body=None):
    get_publisher().not_found(body=body)

def header(title, *args, **kwargs):
    return get_publisher().header(title, *args, **kwargs)

def footer(**kwargs):
    return get_publisher().footer(**kwargs)

def page(title, *content, **kwargs):
    return get_publisher().page(title, *content, **kwargs)

def respond(title, *content, **kwargs):
    return get_publisher().respond(title, *content, **kwargs)

def ensure_signed_in(**kwargs):
    return get_publisher().ensure_signed_in(**kwargs)



