from zope.interface import Interface, Attribute
from sprinkles import ISprinkle
class IWorkspaceItem(ISprinkle):
    
    def fromSystem(cls):
        """ classmethod to return a list of workspace items """

    def serialize(self):
        """ returns a string that can be written to the workspace file """

    def unserialize(cls, s):
        """ classmethod to create an item from its serialized version """

    def load(self):
        """ should load the workspace item to the system """

    def __str__(self):
        """ string repr """
