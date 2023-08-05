"""
A pythonic API to a local subversion repository achieved by wrapping the python
subversion bindings.

@copyright: (c) 2006 Open Knowledge Foundation
@author: Rufus Pollock (Open Knowledge Foundation)
@license: MIT License <http://www.opensource.org/licenses/mit-license.php>
"""
__version__ = '0.1'

import os

import svn.fs
import svn.core
import svn.repos
assert (svn.core.SVN_VER_MAJOR, svn.core.SVN_VER_MINOR) >= (1, 3), "Subversion 1.3 or later required"

class Repository(object):
    """An open subversion repository.

    This class is used to refer to an open repository, and to provide some
    basic features for working with the repository.

    Adapted from subwiki's code produced by greg stein with simplifcations
    due to use of python-svn 1.3

    Also assisted by James Tauber's notes at:

        http://jtauber.com/python_subversion_binding
    
    and trac's wrapper:

        http://trac.edgewall.org/browser/trunk/trac/versioncontrol/svn_fs.py

    Qu: Why not pysvn?
    
    Ans: pysvn is for svn protocol clients, not for interfacing server software
    to the repository layer. It's also all written in C rather than python. I
    therefore didn't explore it any further. 
    """

    def __init__(self, repos_path):
        self.repos_path = repos_path
        self.repos = svn.repos.open(self.repos_path)
        self.fs_ptr = svn.repos.fs(self.repos)

    def youngest_rev(self):
        return svn.fs.youngest_rev(self.fs_ptr)

    def get_revision_property(self, property_name, revision_number):
        return svn.fs.revision_prop(self.fs_ptr, revision_number,
                property_name)

    def get_revision(self, revision_number=None):
        if revision_number is None:
            revision_number = self.youngest_rev()
        log = self.get_revision_property('svn:log', revision_number)
        date = self.get_revision_property('svn:date', revision_number)
        author = self.get_revision_property('svn:author', revision_number)
        root = svn.fs.revision_root(self.fs_ptr, revision_number)
        rev = Revision(log=log, date=date, author=author, root=root,
                repository=self)
        return rev

    def new_revision(self, revision_number=None):
        if revision_number == None:
            revision_number = self.youngest_rev()
        txn = svn.fs.begin_txn(self.fs_ptr, revision_number)
        txn_root = svn.fs.txn_root(txn)
        rev = Revision(root=txn_root, repository=self, txn=txn)
        return rev

    def history(self, path='/'):
        response2 = []
        def collect_logs(paths, number, author, date, log, response=None):
            print 'Hello world'
            response2.insert(0, { 'number': number, 'author' : author, 'date' : date, 'log' : log})
        paths = (path,)

        # svn_repos_get_logs(svn_repos_t repos, apr_array_header_t paths, svn_revnum_t start, 
            # svn_revnum_t end, svn_boolean_t discover_changed_paths, 
            # svn_boolean_t strict_node_history, 
            # svn_log_message_receiver_t receiver, 
            # apr_pool_t pool) -> svn_error_t
        svn.repos.svn_repos_get_logs(self.repos, paths, self.youngest_rev(), 0,
                True, True, collect_logs)
        return response2


class Revision(object):
    """Difficult to create directly best use `Repository.get_new_revision` or
    `Repository.get_revision`
    """

    def __init__(self, root, repository, log='', date=None, author='', txn=None):
        self.root = root
        self.repository = repository
        self.log = log
        self.date = date
        self.author = author
        self.file_system = FileSystem(root, repository)
        self.txn = txn

    def commit(self):
        """Commit this revision.

        @return: a tuple consisting of (msg, new_revision_number) 
        
        svn.fs.commit_txn raises svn.core.SubversionException if a problem.
        """
        svn.fs.change_txn_prop(self.txn, 'svn:log', self.log)
        svn.fs.change_txn_prop(self.txn, 'svn:author', self.author)
        result = svn.fs.commit_txn(self.txn)
        return result

    def abort(self):
        svn.fs.abort_txn(self.txn)

    def get_changeset(self):
        pass


class FileSystem(object):
    """A filesystem associated with a given `Revision`.
    
    Obtained via `Revision.file_system.
    """

    def __init__(self, svnfs, repository):
        self.svnfs = svnfs
        self.repository = repository

    def listdir(self, directory):
        entries = svn.fs.svn_fs_dir_entries(self.svnfs, directory)
        names = entries.keys()
        return names
    
    def make_file(self, path):
        svn.fs.make_file(self.svnfs, path)
        return File(self, path)
    
    def make_dir(self, path):
        """Create a directory.
        @return a `Directory` object for the created directory.
        """
        svn.fs.make_dir(self.svnfs, path)
        return Directory(self, path)
    
    def get_node(self, path):
        raw_node_type = svn.fs.check_path(self.svnfs, path)
        _kindmap = { svn.core.svn_node_dir: Node.DIRECTORY,
                     svn.core.svn_node_file: Node.FILE
                     }
        node_type = _kindmap[raw_node_type]
        if node_type == Node.DIRECTORY:
            return Directory(self, path)
        elif node_type == Node.FILE:
            return File(self, path)
    
    def delete_node(self, path):
        svn.fs.delete(self.svnfs, path)

class Node(object):

    DIRECTORY = 0
    FILE = 1

    def __init__(self, filesystem, path):
        super(Node, self).__init__()
        self.filesystem = filesystem
        self.svnfs = filesystem.svnfs
        self.path = path

    def isdir(self):
        return self.type == Node.DIRECTORY

    def get_property(self, name):
        return svn.fs.node_prop(self.svnfs, self.path, name)

    def set_property(self, name, value):
        svn.fs.change_node_prop(self.svnfs, self.path, name, value) 

    def properties(self):
        """Get a node's properties as a python dictionary.

        @return: a python dictionary consisting of node property (name, value)
        pairs
        
        Note: you cannot edit properties by setting values in the dictionary
        but must use set_property instead.
        """
        property_dict = svn.fs.node_proplist(self.svnfs, self.path)
        return property_dict

    def revision_created(self):
        created = svn.fs.node_created_rev(self.svnfs, self.path)
        return created

    def last_modified(self):
        created = self.revision_created()
        revisionobj = self.filesystem.repository.get_revision(created)
        date = revisionobj.date
        return date

    def history(self):
        return self.filesystem.repository.history(self.path)


class Directory(Node):
    """A directory node in a filesystem.
    """

    type = Node.DIRECTORY


class File(Node):
    """A file node in a `Filesystem`.

    You can obtain the underlying stream (read-only) from the attribute fileobj

    Notes: Bit of a hack at present in that there is an *associated* file object.
    """

    type = Node.FILE

    def __init__(self, svnfs, path):
        super(File, self).__init__(svnfs, path)
        self.fileobj = None
        self._read_fileobj()

    def _read_fileobj(self):
        stream = svn.fs.file_contents(self.svnfs, self.path)
        self.fileobj = svn.core.Stream(stream)

    def write(self, data):
        stream = svn.fs.apply_text(self.svnfs, self.path, None)
        svn.core.svn_stream_write(stream, data)
        svn.core.svn_stream_close(stream)
        # need to reload fileobj as now out of date
        self._read_fileobj()
    
