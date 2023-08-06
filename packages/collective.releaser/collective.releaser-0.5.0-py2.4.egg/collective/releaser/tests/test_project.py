# -*- coding: utf-8 -*-
""" project.py low-level tests
"""
import unittest
import os
import sys
import shutil
import tempfile

from zc.buildout.testing import rmdir

from collective.releaser.project import (archive_contents, _python, 
                                 diff_releases, _set_dynlibs, 
                                 _extract_url,  _make_python,
                                 copy_archives, build_md5, project_eggs)
from collective.releaser import testing
from collective.releaser import base

from os.path import join
curdir = os.path.dirname(__file__)

class ProjectTest(unittest.TestCase):
  
    globs = {}
 
    def setUp(self):
        testing.releaserSetUp(self)
        testing.clearRepository(self)

        # adding a 'previous' snap
        svn_root = '%s/sample-buildout/trunk' % self.globs['svn_url']
        previous_snap = ['eggs/file', 'eggs/stuff.egg',
                         'downloads/dist/file', 'downloads/dist/file2']
        self.svn_root = svn_root

    def tearDown(self):
        testing.releaserTearDown(self)
     
    def test_light_archiving(self):

        location = join(os.path.dirname(__file__), 'tarball')
        tarfile_ = join(os.path.dirname(__file__), 'pack.tgz')
        
        x = [join(location, path) for path in 
             ['parts', 'var', 'develop-eggs', 'bin', 'lib',
              'Lib', 'Scripts', join('downloads', 'dist')]]

        # light archiving
        archive_contents('pack.tgz', location, source=True, exclude=x) 
        import tarfile
        tar = tarfile.open(tarfile_, "r:gz")
        try:
            elements = [tarinfo.name for tarinfo in tar
                        if not os.path.split(tarinfo.name)[-1].startswith('.')]
        finally:
            tar.close()

        for el in ['downloads/file.pyc', 'file2.pyc', 'file3.pyo']:
            self.assert_(el not in elements)
        
        # make sure we don't have downloads/dist files and Scripts/ ones:
        #for el in ['downloads/dist/file', 'Scripts/a_script']:
        for el in ['Scripts/a_script']:
            self.assert_(el not in elements)

        os.remove(tarfile_)

        # complete archiving
        archive_contents('pack.tgz', location, source=False) 
        import tarfile
        tar = tarfile.open(tarfile_, "r:gz")
        try:
            elements = [tarinfo.name for tarinfo in tar
                        if not os.path.split(tarinfo.name)[-1].startswith('.')]
        finally:
            tar.close()

        wanted = ['downloads/dist/file', 'downloads/dist/file.py', 
                  'downloads/dist/file2', 'downloads/file.pyc', 
                  'downloads/file2', 'eggs/file', 'eggs/stuff.egg/file', 
                  'file', 'file2.pyc', 'file3.pyo'] 
       
        wanted.sort()
        elements.sort()
        self.assertEquals(elements, wanted)

        os.remove(tarfile_)
    
    def test_archiving(self): 
        location = join(os.path.dirname(__file__), 'tarball')
        #previous = self.svn_root
        tarfile_ = join(os.path.dirname(__file__), 'pack.tgz')
        archive_contents('pack.tgz', location) 
    
        # checking the result
        import tarfile
        tar = tarfile.open(tarfile_, "r:gz")
        try:
            elements = [tarinfo.name for tarinfo in tar
                        if not os.path.split(tarinfo.name)[-1].startswith('.')]
        finally:
            tar.close()

        for el in ['downloads/file2', 'file']:
            self.assert_(el in elements)

        os.remove(tarfile_)

    def test_python(self):
        # virtualenv generates python either python2.4
        test_bin = join(os.path.dirname(__file__), 
                                'test_bin')
        os.mkdir(test_bin)
        os.chdir(test_bin)
        try:
            os.mkdir(join(test_bin, 'bin'))
            os.mkdir(join(test_bin, 'Scripts'))
            linux =  (('bin', 'python'), 
                      ('bin', 'python2.4'),
                      ('bin', 'python2.4.3'))
            windows = (('Scripts', 'python.exe'),)
            if sys.platform == 'win32': 
                places = windows
            else:
                places = linux

            for place in places:
                f = open(join(test_bin, place[0], place[1]), 'w')
                f.write('#')
                f.close()
                python = _python()    
                self.assertEquals(python, join(place[0], place[1]))
                os.remove(python)
        finally:
            shutil.rmtree(test_bin)

    def test_diff_releases(self):
        # making a new tarball diff
        diff_dir = join(os.path.dirname(__file__), 'diff')
        old = join(diff_dir, 'old.tgz')
        new = join(diff_dir, 'new.tgz')
        res = join(diff_dir, 'res.tgz') 
        wanted = join(diff_dir, 'diff.tgz')
        try:
            diff_releases(old, new, res)

            # let's compare
            self.assert_(open(res, 'wb'), open(wanted, 'wb'))
        finally:
            if os.path.exists(res):
                os.remove(res)
    
    def test_diff_releases2(self):
        # make sure we get the tarball named autoamtically
        # in the right place
        diff_dir = join(os.path.dirname(__file__), 'diff')
        old = join(diff_dir, 'old.tgz')
        new = join(diff_dir, 'new.tgz')
        res = join(diff_dir, 'old-to-new.tgz') 
        wanted = join(diff_dir, 'diff.tgz')
        try:
            diff_releases(old, new)
            # let's compare
            self.assert_(open(res, 'wb'), open(wanted, 'wb'))
        finally:
            if os.path.exists(res):
                os.remove(res)

    def test_set_dynlibs(self):
        old = sys.executable
        sys.executable = os.path.join(curdir, 'python', 'python.exe')
        try:
            root = os.path.join(curdir, 'root')
            _set_dynlibs(root)
            self.assert_(os.path.exists(os.path.join(root, 'libs', 
                                                      'libpython24.a')))
        finally:
            shutil.rmtree(os.path.join(root, 'libs'))
            sys.executable = old

    def test_extract_url(self):
    
        prot, path = _extract_url('http://svn.ingeniweb.com/pack')
        self.assertEquals(prot, 'http://')
        self.assertEquals(path, ['svn.ingeniweb.com', 'pack'])

        prot, path = _extract_url('https://svn.ingeniweb.com/pack')
        self.assertEquals(prot, 'https://')
        self.assertEquals(path, ['svn.ingeniweb.com', 'pack'])

        prot, path = _extract_url('svn://svn.ingeniweb.com/pack')
        self.assertEquals(prot, 'svn://')
        self.assertEquals(path, ['svn.ingeniweb.com', 'pack'])
    
    def test_make_python(self):
        python = _make_python(curdir)
        try:
            self.assert_(os.path.exists(python)) 
        finally:
            if os.path.exists(python):
                dir_ = os.path.dirname(python)
                shutil.rmtree(dir_)
                
    def test_copy_archives(self):
       
        source = join(os.path.dirname(__file__), 'tarball')
        target = join(os.path.dirname(__file__), 'tarball2')
        os.mkdir(target)
        os.mkdir(join(target, 'downloads'))
        os.mkdir(join(target, 'eggs'))

        try:
            copy_archives(source, target)
            # eggs is not touched because the source doesn't have it
            # downloads existed on the target, so it is renamed
            res = ['downloads', 'downloads_old', 'eggs', 'eggs_old']
            res.sort()
            t = os.listdir(target)
            t.sort()
            self.assertEquals(t, res)
            
            downloads = os.listdir(join(target, 'downloads'))
            downloads.sort()
            self.assertEquals(downloads, ['dist', 'file.pyc', 'file2'])
        finally:
            shutil.rmtree(target)
                
    def test_build_md5(self):
        source = join(os.path.dirname(__file__), 'tarball')
        md5 = build_md5(source)
        # let's change a file
        file_ = join(source, 'downloads', 'dist', 'file.py')
        old_content = open(file_).read()
        try:
            open(file_, 'w').write('xxxxxx')
            new_md5 = build_md5(source)  
            self.assertNotEqual(new_md5, md5)
        finally:
            open(file_, 'w').write(old_content)

    def XXXtest_project_eggs(self):
        
        def _list_tarball(tarball):
            import tarfile
            s = os.path.split
            tar = tarfile.open(tarball, "r:gz")
            try:
                elements = [t.name for t in tar
                            if not s(t.name)[-1].startswith('.')]
            finally:
                tar.close()
            elements.sort()
            return elements

        project = join(os.path.dirname(__file__), 'buildout')
        tarball = join(os.path.dirname(__file__), 'res.tgz') 
        eggs =  project_eggs(join(project, 'buildout.cfg'), tarball)
        
        self.assert_(eggs[0].startswith('iw.fss'))
        self.assert_(eggs[-1].startswith('zc.recipe.egg'))

        # testing with installation
        folder = tempfile.mkdtemp()
        try: 
            eggs =  project_eggs(join(project, 'buildout.cfg'), tarball) 

            # what do we have
            res = _list_tarball(tarball)
            self.assertEquals(res[0], 'another.cfg')
            self.assert_('iw.fss' in res[10])
        finally:
            shutil.rmtree(folder, ignore_errors=True)
            if os.path.exists(tarball):
                os.remove(tarball)

        # testing filtering
        folder = tempfile.mkdtemp()
        try: 
            eggs =  project_eggs(join(project, 'buildout.cfg'), tarball,
                                 ('iw.f*',)) 
            # what do we have
            res = _list_tarball(tarball)
            self.assert_('iw.fss' in res[-1])
        finally:
            shutil.rmtree(folder, ignore_errors=True)
            if os.path.exists(tarball):
                os.remove(tarball)


def test_suite():
    """returns the test suite"""
    return unittest.makeSuite(ProjectTest)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


