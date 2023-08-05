"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/ui/directory.py $
$Id: directory.py 27324 2005-09-07 18:28:21Z rmasse $
"""
from quixote import get_request, redirect, get_path, get_user
from dulcinea.ui.errors import not_found
from dulcinea.ui.util import index_page

class DynamicExportingDirectory (object):

    def _q_translate(self, component):
        """(component : string) -> string | None
        """
        for export, name, crumb, title in self.get_exports():
            if component == export:
                return name
        return None

    def _q_lookup(self, component):
        """(component : string) -> object

        Lookup a path component and return the corresponding object (usually
        a Directory, a method or a string).  Returning None signals that the
        component does not exist.
        """
        return None

    def _q_traverse(self, path):
        """(path: [string]) -> object

        Traverse a path and return the result.
        """
        component = path[0]
        name = self._q_translate(component)
        if name is None:
            obj = self._q_lookup(component)
        else:
            obj = getattr(self, name)
        if obj is None:
            print '\n404: %r has no component %r; PATH=%s; USER=%s' % (
                self, name, get_path(), get_user())
            not_found()
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
        if (self._q_translate('') is not None and
            not get_request().get_fields()):
            # Fix missing trailing slash.
            return redirect(get_path() + "/", permanent=True)
        else:
            return None

    def _q_index(self):
        return index_page(self)
