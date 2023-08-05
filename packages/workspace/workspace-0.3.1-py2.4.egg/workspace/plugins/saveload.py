from zope.interface import implements
from workspace.interfaces import IWorkspaceCommand
from workspace.core import Workspace

class LoadCommand(object):
    implements(IWorkspaceCommand)
    
    @classmethod
    def canHandle(cls, cmd):
        return cmd == "load"

    def handle(self, args):
        ws = Workspace.fromFile('.workspace')
        for k, v in ws.data.iteritems():
            for d in v.data:
                d.load()

class SaveCommand(object):
    implements(IWorkspaceCommand)
    
    @classmethod
    def canHandle(cls, cmd):
        return cmd == "save"

    def handle(self, args):
        ws = Workspace.fromSystem()
        f = open('.workspace', 'w')
        f.write(str(ws))
        f.close()
