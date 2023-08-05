"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/fill/directory.py $
$Id: directory.py 26642 2005-04-21 18:23:06Z dbinger $
"""
import sys
from qp.pub.common import get_request, get_path, redirect, not_found, get_path
from qp.pub.common import get_response


class Directory (object):
    """
    Subclasses of this class define the publishing traversal through
    one '/' of a url.  Usually, this involves overriding get_exports()
    and providing a method for each name that you want to export.
    Note that '' can be, and usually is, exported like any other.
    If your class includes a _q_index() method to provide the response
    for urls that end at this '/', then the result of get_exports() should
    include ('', '_q_index', None, None).
    """

    def get_exports(self):
        """Returns an iterable of 4 tuples:
        (path_component:str,
         attribute_name:str|None,
         crumb:str|None,
         title:str|None)

        Subclasses normally override this to provide the explicit exports.

        The crumb and title parameters allow you to specify what links to this
        export should look like.  The crumb value is used as the content of the
        link.  The title value is use as the title attribute of the link.

        When the attribute_name is None, the _q_lookup should provide a result
        for that path_component.
        """
        return []

    def _q_translate(self, component):
        """(component : string) -> string|None

        Returns the name of the attribute exported for the given path component,
        or None.  Subclasses will not normally need to override this.
        """
        for export, name, crumb, title in self.get_exports():
            if component == export:
                return name
        return None

    def _q_lookup(self, component):
        """(component : string) -> object

        Lookup a path component and return the corresponding object
        (usually a Directory, a method or a string).
        Returning None signals that the component does not exist.

        Subclasses should override this when they want to export path
        components that, for one reason or another, don't have corresponding
        attributes that can be found using _q_translate.  This happens,
        for example, when you want to export the set of all integers or other
        large sets.
        """
        return None

    def _q_traverse(self, path):
        """(path: [string]) -> None|Stream|object

        Traverse a path and return the result.  This is what the
        Publisher calls.  The result will be used to set the body of
        the http response.  If the result is None, the Publisher will
        use not_found() to set the 404 response.  If the result is an
        instance of Stream, it will be written out in in chunks.
        Otherwise, the str() of the result of this call will be used
        as the body of the http response.

        Subclasses don't normally need to override this, but may do so.
        This may be useful to provide access control or to implement
        directories that process the entire path themselves.
        """
        component = path[0]
        name = self._q_translate(component)
        if name is None:
            obj = self._q_lookup(component)
        else:
            obj = getattr(self, name)
        if obj is None:
            not_found('%r?' % component)
        if path[1:]:
            if hasattr(obj, '_q_traverse'):
                result = obj._q_traverse(path[1:])
            else:
                not_found()
        elif callable(obj):
            result = obj()
        else:
            result = obj
        if result is None:
            not_found()
        else:
            return result

    def __call__(self):
        """() -> None|Stream|object
        If the _q_traverse() of a Directory reaches this instance,
        and there are no more components, it calls this instance.
        We could return None to cause a 404 response, but we'll try
        adding a slash to the end of the url if it looks like that
        appears to be the intent of the current request.
        """
        if (self._q_translate('') is not None and
            not get_request().get_fields()):
            # Fix missing trailing slash.
            return redirect(get_request().get_path_info() + "/", permanent=True)
        else:
            return None


def get_directory_path():
    """() -> [object]
    Return the list of traversed instances.
    Thus uses the frame stack, so it is only meaningful in the context of a call
    to _q_traverse.
    """
    path = []
    frame = sys._getframe()
    while frame:
        if frame.f_code.co_name == '_q_traverse':
            self = frame.f_locals.get('self', None)
            if path[:1] != [self]: # avoid repetition
                path.insert(0, self)
        frame = frame.f_back
    return path


def get_path_directory_list():
    """() -> [(relative_path:str, directory:Directory)]
    Provides a relative path for each directory currently traversed.
    """
    app_root = get_request().get_environ('SCRIPT_NAME', '')
    path = get_path()
    path_components = path[len(app_root):].split('/')
    namespace_stack = get_directory_path()
    if get_response().get_status_code() == 200:
        offset = -1
    else:
        offset = 0
    return [('./' + '../' * (len(namespace_stack) - k + offset),
             namespace_stack[k])
            for k in range(min(len(path_components), len(namespace_stack)))]

def get_crumb_tree():
    """() - > [[(path:str, crumb:str, title:str)]]
    Each list in the result is a menu of exports for a directory on the
    current path.
    """
    crumb_tree = []
    for path, directory in get_path_directory_list():
        menu = []
        for component, name, crumb, title in directory.get_exports():
            if crumb: # skip crumbs and menus if no crumb
                if component == '':
                    menu.insert(0, (path + component, crumb, title))
                else:
                    menu.append((path + component, crumb, title))
            elif component == '':
                menu = []
                break
        if menu:
            crumb_tree.append(menu)
    return crumb_tree




