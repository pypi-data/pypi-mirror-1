from zope.interface import Interface, Attribute, implements
import sprinkles
from workspace.interfaces import IWorkspaceSection
from workspace.plugins.items_interfaces import IWorkspaceItem

class ItemsSection(object):
    implements(IWorkspaceSection)
    data = []
    name = "items"
    
    def __init__(self):
        self.types = sprinkles.fromPackage('workspace.plugins', 
                                           IWorkspaceItem.implementedBy)

    def append(self, i):
        self.data.append(i)
    
    @classmethod
    def fromSystem(cls):
        print "items formSystem"
        self = cls()
        print "items types", self.types
        for t in self.types:
            d = t.fromSystem()
            for x in d:
                self.append(x)
        return self
            

    @classmethod
    def canHandle(cls, name):
        if name == cls.name:
            return True
        return False

    def getItem(self, l):
        if type(l) is type(""):
            name = l.split(":")[0]
            for t in self.types:
                if t.name == name:
                    return t.unserialize(l)
        return None
