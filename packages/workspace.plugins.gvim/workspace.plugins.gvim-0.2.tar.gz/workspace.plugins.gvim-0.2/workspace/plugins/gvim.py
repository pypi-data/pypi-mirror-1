from zope.interface import implements
#from workspace.plugins.items import IWorkspaceItem
from workspace.plugins.items_interfaces import IWorkspaceItem
import re
import commands
import os

class GvimItem(object):
    implements(IWorkspaceItem)
    name = "gvim"
    
    def __init__(self, files, cwd=None):
        self.files = files
        self.cwd = cwd

    @classmethod
    def fromSystem(cls):
        print "gvim fromSystem"
        """ return an array of GvimItems """
        pids = commands.getoutput(r"""ps awx | grep Vim | grep -v grep | awk '{print $1}'""")
        pids = pids.split()
        #print pids
        return [cls._fromPID(p) for p in pids]

    def serialize(self):
        return "%s:%s:%s"%(self.name, self.cwd, ":".join(self.files))

    @classmethod
    def unserialize(cls, s):
        parts = s.split(":")
        return cls(parts[2:], cwd=parts[1])

    def load(self):
        last = os.getcwd()
        os.chdir(self.cwd)
        
        os.spawnlp(os.P_NOWAIT, 'gvim', 'gvim', *self.files)
        os.chdir(last)

    def __str__(self):
        return self.serialize()


    """ internal """
    re_grep_swap = re.compile(r"""\.swp""")
    re_swap = re.compile(r""".* (/.*/)\.(.*)\.swp$""")
    re_grep_cwd = re.compile(r"""\scwd\s""")
    re_cwd = re.compile(r""".* (\/.*)*""")

    @classmethod
    def _fromPID(cls, pid):
        lsof = commands.getoutput("lsof -p %s"%(pid))
        lsof = lsof.split("\n")
        swapFiles = [cls.re_swap.sub(r"\1\2", x) for x in lsof
                     if cls.re_grep_swap.search(x)]
        #for x in lsof:
        #    print cls.re_grep_swap.search(x)
        #print swapFiles
        cwd = [cls.re_cwd.sub(r"\1", x) for x in lsof
               if cls.re_grep_cwd.search(x)]
        #print cwd
        return cls(swapFiles, cwd=cwd[0])

