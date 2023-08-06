from pyutilib.plugin import *

class IPackage1Util(Interface):
    """Interface for Package1 utilities"""


class Package1Util(SingletonPlugin):

    implements(IPackage1Util)

