import random
import shutil
import commands
import datetime

import py.test

from svnrepo import *

repos_path = os.path.abspath('./demorepo')
class TestSvnBase(object):

    def setup_class(cls):
        # we tear down here rather than in a teardown method so we can
        # investigate if things go wrong
        if os.path.exists(repos_path): 
            shutil.rmtree(repos_path)
        cmd1 = 'svnadmin create %s' % repos_path
        cmd2 = 'svn mkdir file://%s -m "%s"' % (os.path.join(repos_path, 'tmp'),
                'Adding /tmp dir.')
        cmd3 = 'svn mkdir file://%s -m "%s"' % (os.path.join(repos_path,
            'todelete'),
                'Adding /tmp dir.')
        status, output = commands.getstatusoutput(cmd1)
        print output
        if status:
            raise Exception(output)
        status, output = commands.getstatusoutput(cmd2)
        if status:
            raise Exception(output)
        status, output = commands.getstatusoutput(cmd3)
        if status:
            raise Exception(output)
        cls.repos = Repository(repos_path)


class TestRepository(TestSvnBase):

    def test_youngest_rev(self):
        revnum = self.repos.youngest_rev()
        assert revnum >= 0

    def test_get_revision(self):
        rev = self.repos.get_revision(1)
        assert len(rev.log) > 0
        assert '200' in rev.date
        assert len(rev.author) > 0
    
    def test_history(self):
        history = self.repos.history('/')
        assert len(history) > 0
        count = 0
        for rev in history:
            print rev
            assert rev['number'] == count
            count += 1

class TestRevision(TestSvnBase):

    def test_file_system(self):
        rev = self.repos.get_revision(1)
        fs = rev.file_system
        dirlist = fs.listdir('/')
        assert 'tmp' in dirlist

    def test_create_revision(self):
        """
        This tests a lot including:
            Repository.new_revision()
            Filesystem....
        """
        newrev = self.repos.new_revision()
        newrev.log = 'My new revision'
        newrev.author = 'me'
        fs = newrev.file_system
        filepath = 'tmp.txt'
        newfile = fs.make_file(filepath)

        text = 'nothing ever exists entirely alone'
        newfile.write(text)

        propname = 'copyright'
        propval = 'nemo'
        newfile.set_property(propname, propval)

        newrev.commit()

        # now get the latest revision and check it
        rev = self.repos.get_revision()
        assert rev.log == newrev.log
        assert rev.author == newrev.author
        assert '200' in rev.date
        dirlist = rev.file_system.listdir('/')
        assert filepath in dirlist
        fileout = rev.file_system.get_node(filepath)
        fileobj = fileout.fileobj
        assert fileobj.read() == text
        assert fileout.get_property(propname) == propval
    
    def test_create_conflicting_revisions(self):
        newrev1 = self.repos.new_revision()
        newrev2 = self.repos.new_revision()
        def alter_rev(newrev):
            fs = newrev.file_system
            filepath = 'conflict.txt'
            newfile = fs.make_file(filepath)
            newfile.write('blah')
            msg, status = newrev.commit()
            return status
        assert alter_rev(newrev2) > 0
        import svn.core
        py.test.raises(svn.core.SubversionException, alter_rev, newrev1)


class TestNode(TestSvnBase):

    def test_isdir(self):
        rev = self.repos.get_revision(1)
        fs = rev.file_system
        rootdir = fs.get_node('/')
        assert rootdir.isdir()

    def test_properties(self):
        propname = 'random'
        propval = 'annakarenina'
        newdirpath = '/property_test'
        newrev = self.repos.new_revision()
        fs = newrev.file_system
        newdir = fs.make_dir(newdirpath)
        newdir.set_property(propname, propval)
        properties = newdir.properties()
        out1 = newdir.get_property(propname)
        assert out1 == propval
        assert properties[propname] == propval
        # setting values in properties dictionary won't affect svn node
        # properties[propname] = 'warandpeace'
        # out1 = newdir.get_property(propname)
        # assert out1 == 'warandpeace' # FAILS
        newrev.commit()
        latestrev = self.repos.get_revision()
        newdir2 = latestrev.file_system.get_node(newdirpath)
        pp = newdir2.properties()
        out2 = newdir2.get_property(propname)
        assert pp[propname] == propval
        assert out2 == propval 
    
    def test_revision_created(self):
        rev = self.repos.get_revision()
        tmpdir = rev.file_system.get_node('/tmp')
        out = tmpdir.revision_created()
        assert out == 1

    def test_last_modified(self):
        rev = self.repos.get_revision()
        tmpdir = rev.file_system.get_node('/tmp')
        out = tmpdir.last_modified()
        year = str(datetime.datetime.now().year)
        assert out.startswith(year)

    def test_history(self):
        rev = self.repos.get_revision()
        tmpdir = rev.file_system.get_node('/tmp')
        history = tmpdir.history()
        # tmpdir was created in revision and nothing has happened to it since
        assert len(history) == 1
        assert history[0]['number'] == 1


class RepoStub(object):

    def __init__(self, path):
        self.path = path
        self.repo = Repository(path)
        self._make_rev1()
        self._make_rev2()

    def _make_rev1(self):
        newrev = self.repo.new_revision()
        newrev.log = 'Revision number 1'
        newrev.author = 'me'
        fs = newrev.file_system
        newfile = fs.make_file('/rev1.txt')
        newfile.write('blah')
        newrev.commit()
    
    def _make_rev2(self):
        pass

