
import pyutilib
from pyutilib.plugin import *

class IExternalExecutable(Interface):
    """Interface for plugins that define an external executable"""

    def get_path(self):
        """Returns a string that is the path of the executable"""


class ExternalExecutable(Plugin):
    
    implements(IExternalExecutable)

    def __init__(self,**kwds):
        if 'doc' in kwds:
            self.exec_doc = kwds["doc"]
        else:
            self.exec_doc = ""
        if 'name' in kwds:
            self.name = kwds['name']
            declare_option(kwds['name'], local_name="executable", section="executables", default=None, doc=self.exec_doc, cls=ExecutableOption)
        else:
            raise PluginError("An ExternalExectuable requires a name")
        if 'path' in kwds:
            self.exec_default = kwds["path"]
        else:
            self.exec_default = pyutilib.search_file(self.name,
                                implicitExt=pyutilib.executable_extension,
                                executable=True)

    def enabled(self):
        return self._enable and ((self.executable is not None) or (self.exec_default is not None))

    def get_path(self):
        if not self.enabled():
            return None
        tmp = self.executable
        if tmp is None:
            return self.exec_default
        return tmp

