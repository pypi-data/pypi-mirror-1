from zope.interface import Interface, Attribute, implements
from sprinkles import ISprinkle
class IWorkspaceSection(ISprinkle):
    name = Attribute("""the section name""")
    def append(self, l):
        """parse in a new line"""
    
    def canHandle(cls, name):
        """ called to see if this sction handles the given section heading """


class IWorkspaceCommand(ISprinkle):
    def canHandle(cls, cmd):
        """ called to check whether the given parser can handle the stuffs"""

    def handle(self, args):
        """ executes the given command """
