import os
from mercurial import hg, ui, patch
from mercurial.node import hex, short as short_hex, bin as short_bin
from mercurial.localrepo import localrepository
from mercurial.node import nullid
from buildtree import RevGraph
from StringIO import StringIO
import textwrap
import time
import mercurial.commands
import mercurial.cmdutil
import re

try:
    # try to use new API (hg 1.1)
    matchfiles = mercurial.cmdutil.matchfiles
    def pdiff(repo, node1, node2, match):
        return "\n".join(patch.diff(repo, node1=node1, node2=node2, match=match))
    
except AttributeError:
    ## work with version 1.0.1
    def matchfiles(repo, files):
        def match(filename, files=files):
            return filename in files
        return match

    def pdiff(repo, node1, node2, match):
        out = StringIO()
        patch.diff(repo, node1=node1,
                   node2=node2, match=match, fp=out)
        return out.getvalue()

class RevNode(object):
    __slots__ = "rev author_id desc localtime files tags branches".split()
    
    def __init__(self, rev, author_id, desc, date, files, tags, branches):
        self.rev = rev
        self.author_id = author_id
        self.desc = desc.strip()+"\n"
        #self.desc = desc
        self.localtime = date
        self.files = tuple(files)
        self.tags = tags
        self.branches = branches

    def get_short_log( self ):
        """Compute a short log from the full revision log"""
        offs = self.desc.find('\n')
        if offs>0:
            text = self.desc[:offs]
        else:
            text = "*** no log"
        return text
    short = property(get_short_log)

    def get_date( self ):
        date_ = time.strftime( "%Y-%m-%d %H:%M", self.localtime )
        return date_
    date = property(get_date)
    

class Repository(object):
    """Abstract interface for a repository"""
    def __init__(self, path):
        """path : path of repository"""
        self.dir = self.find_repository( path )
        # The list of authors names
        self.authors = []
        # colors for the authors (need to get out of here)
        self.colors = []
        # the list of nodes
        self.nodes = []

    def find_repository(cls, path):
        """finds the root repository or raises
        its a class method so one can use it to find
        the best (closest to path) repo for a given
        type of repository
        """
        raise NotImplementedError()
    find_repository = classmethod( find_repository )


    def read_node( self, nodeid ):
        """Returns the node's attributes as RevNode instance"""
        raise NotImplementedError()

    def parents( self, node ):
        """Returns a list of parents' ids for the node"""
        raise NotImplementedError()

    def children( self, node ):
        """Returns a list of children's ids for the node"""
        raise NotImplementedError()

    def diff( self, node1, node2, files ):
        """Returns a diff between node1 and node2 for the
        files listed in files"""
        raise NotImplementedError()

    def count( self ):
        """Returns the number of nodes"""
        raise NotImplementedError()

    def graph( self, nodes ):
        """Returns a graph object allowing representation
        of the tree of revisions reduced to 'nodes'
        """

    def add_tag( self, rev, label ):
        pass

    def get_branches(self):
        """
        return branches
        """

    def get_branches_heads(self):
        """
        return branch heads
        """
  
# A default changelog_cache node
EMPTY_NODE = (-1,  # REV num
              "",  # short desc
              -1,  # author ID
              "",  # full log
              "",  # Date
              (),  # file list
              [],  # tags
              [],  # branches
              )


COLORS = [ "blue", "darkgreen", "red", "green", "darkblue", "purple",
           "cyan", "magenta" ]

class HgHLRepo(object):
    """high level operation on a mercurial repo
    """
    def __init__(self, path):
        self.dir = self.find_repository( path )
        self.ui = ui.ui()
        self.repo = hg.repository( self.ui, self.dir )
        # cache and indexing of changelog
        self._cache = {}

    def refresh(self):
        self.repo = hg.repository( self.ui, self.dir )
        
    def get_branch(self):
        return self.repo.branchtags()

    def get_branches_heads(self):
        return self.repo._readbranchcache()


    def find_repository(self, path):
        """returns <path>'s mercurial repository

        None if <path> is not under hg control
        """
        path = os.path.abspath(path)
        while not os.path.isdir(os.path.join(path, ".hg")):
            oldpath = path
            path = os.path.dirname(path)
            if path == oldpath:
                return None
        return path
    find_repository = classmethod( find_repository )

    def read_nodes(self):
        """Read the nodes of the changelog"""
        changelog = self.repo.changelog
        # we do not use new 1.1 API in which self.repo is iterable for
        # the sake of compatibility
        self.nodes = [changelog.node(i) for i in xrange(self.count())]
        self._cache = {}
        self.authors = []
        self.branches =[]
        self.colors = []
        self.branchcolors = []
        self.authors_dict = {}
        self.branches_dict = {}

    def read_node( self, node ):
        """Gather revision information from mercurial"""
        nodeinfo = self._cache
        if node in nodeinfo:
            return nodeinfo[node]
        NCOLORS = len(COLORS)
        changelog = self.repo.changelog
        _, author, date, filelist, log, branches = changelog.read( node )
        bid = len(branches['branch'])
        branch = branches['branch']
        branch_id = self.branches_dict.setdefault( branch, bid )
        if branch_id == bid:
            self.branches.append( branch )
            self.branchcolors.append( COLORS[bid%NCOLORS] )
        rev = changelog.rev( node )
        aid = len(self.authors)
        author_id = self.authors_dict.setdefault( author, aid )
        if author_id == aid:
            self.authors.append( author )
            self.colors.append( COLORS[aid%NCOLORS] )
        filelist = [ intern(f) for f in filelist ]
        date_ = time.localtime(date[0])
        taglist = self.repo.nodetags(node)
        tags = ", ".join(taglist)
        _node = RevNode(rev, author_id, log, date_, filelist, tags, branches)
        nodeinfo[node] = _node
        return _node

    def graph( self, todo_nodes ):
        return RevGraph( self.repo, todo_nodes, self.nodes )

    def parents( self, node ):
        parents = [ n for n in self.repo.changelog.parents(node) if n!=nullid ]
        if not parents:
            parents = [nullid]
        return parents

    def children( self, node ):
        return [ n for n in self.repo.changelog.children( node ) if n!=nullid ]
    
    def diff(self, parents, node2, files):
        fmatch = matchfiles(self.repo, files)
        changes = self.repo.status(parents[0], node2, match=fmatch)[:4]
        modified, added, removed, deleted = changes
        # find renamed files
        files = list(files[:])
        diffmsg = ""
        ctx = self.repo.changectx(node2)
        for f in added:
            fctx = ctx.filectx(f)
            m = fctx.filelog().renamed(fctx.filenode())
            if m:
                diffmsg += "%s renamed from %s:%s\n" % (f, m[0], hex(m[1]))
                files.remove(f)
                files.remove(m[0])
        if len(parents)==1:
            return diffmsg , self.single_diff(parents[0], node2, files), changes
        else:
            #Fix: merge_diff don't work, temporary we will use single_diff in the both cases
            ##return self.merge_diff( parents, node2, files )
            return diffmsg , self.single_diff(parents[0], node2, files), changes

    def single_diff( self, node1, node2, files):
        m = matchfiles(self.repo, files)
        return pdiff(self.repo, node1=node1, node2=node2, match=m)

    def merge_diff( self, parents, node2, files ):
        s = ""
        assert len(parents)==2
        ancestor = self.repo.changelog.ancestor( parents[0], parents[1] )
        for f in files:
            d0 = self.single_diff( parents[0], node2, [f] )
            d1 = self.single_diff( parents[1], node2, [f] )
            p0 = self.single_diff( ancestor, parents[0], [f] )
            p1 = self.single_diff( ancestor, parents[1], [f] )
            op0 = self.get_ops( p0 )
            od0 = self.get_ops( d0 )
            for op in od0:
                self.apply_ops( op0, *op )
            op1 = self.get_ops( p1 )
            od1 = self.get_ops( d1 )
            for op in od1:
                self.apply_ops( op1, *op )
        return s

    def count( self ):
        try:
            # for hg 1.1
            return len(self.repo.changelog)
        except:
            # old API (hg <= 1.0)
            return self.repo.changelog.count()

    def get_ops( self, udiff ):
        hunk = None
        ops = []
        for l in udiff.splitlines():
            if l.startswith("diff"):
                hunk = None
                continue
            if l.startswith("@@"):
                tmp = l.split("@@")[1].split()
                tmp2 = tmp[0][1:].split(",")
                tmp3 = tmp[1][1:].split(",")
                hunk = [ int(x) for x in tmp2+tmp3 ]
                continue
            if not hunk:
                continue
            ob, ol, nb, nl = hunk
            if l.startswith("+"):
                ops.append( [l, ob, nb] )
                hunk[2]+=1
            elif l.startswith("-"):
                ops.append( [l, ob, nb] )
                hunk[0]+=1
            else:
                hunk[0]+=1
                hunk[2]+=1

        return ops

    def apply_ops( self, ops, line, nob, nnb ):
        i = 0
        while i < len(ops):
            if nob>=ops[i][2]:
                i = i+1
                continue
            break

        deltaorig = 0
        if i==0 and nob>ops[0][2]:
            pass
        elif 0<i:
            deltaorig = ops[i-1][2]-ops[i-1][1]

        ops.insert(i, [line, nob-deltaorig, nnb-deltaorig] )
        if line[0]=="+":
            delta = +1
        else:
            delta = -1
        for t in ops[i+1:]:
            t[2]+=delta
        
    def add_tag( self, rev, label ):
        mercurial.commands.tag( self.ui, self.repo, label,
                                rev=1, message="hop",
                                local=True, user=None, date=None )


if __name__ == "__main__":
    import sys
    rep = HgHLRepo(sys.argv[1])
    
