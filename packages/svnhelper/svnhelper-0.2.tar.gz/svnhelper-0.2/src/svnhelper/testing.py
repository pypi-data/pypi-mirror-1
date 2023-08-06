# -*- coding: utf-8 -*-
from utils import get_binary
from utils import sh
from utils import *
import tempfile
import shutil
import sys
import os
import re

svn_normalizer = [
    (re.compile(
        '(.*\s%(sep)s|%(sep)s).*svnhelper_\S+_tmpDir(.*)' % {'sep':os.sep}),
     '\\1virtualenv\\2'),
    (re.compile(
        '(.*\s%(sep)s|%(sep)s).*svnhelper_\S+_tmpPackage(.*)' % {'sep':os.sep}),
     '\\1package\\2'),
    (re.compile('(.*)Python(.*)'),
     '\\1python\\2'),
    (re.compile('(.*file://).*/svnhelper_\S+_tmpRepository/(.*)'),
     '\\1/\\2'),
    (re.compile('URL :(.*)'),
     'URL:\\1'),
    (re.compile('Repository UUID:.*'),
     'Repository UUID: XXXXX-XXXX-XXX'),
]

def mkrepos():
    dirname = tempfile.mkdtemp('_tmpRepository','svnhelper_')
    svnadmin = get_binary('svnadmin')
    repos = os.path.join(dirname, 'test_repos')
    sh(svnadmin, 'create', repos)
    return repos

def rmrepos(dirname):
    shutil.rmtree(dirname)
    dirname, repos = os.path.split(dirname)
    if repos == 'test_repos':
        shutil.rmtree(dirname)

def remove_svn_dirs(dirname):
    for root, dirs, files in os.walk(dirname):
        for dirname in dirs:
            if dirname == '.svn':
                shutil.rmtree(os.path.join(root, dirname))

def setUpRepository(test):
    repos = mkrepos()
    dirname, d = os.path.split(repos)
    repos_url = 'file://%s' % repos
    test.globs['__test_dirs'] = [dirname]
    test.globs['repository'] = repos_url
    test.globs['__executable'] = sys.executable


    def init_test_package(dirname, cleaned=True):
        dirname, package = create_tree(dirname, ignore_structure=True)
        if cleaned:
            remove_svn_dirs(dirname)
        test.globs['__test_dirs'].append(dirname)
        test.globs['package_dir'] = os.path.join(dirname, package)

    test.globs['init_test_package'] = init_test_package

    def import_test_package(dirname):
        init_test_package(dirname, True)
        os.chdir(test.globs['package_dir'])
        import svnhelper
        svnhelper.import_to(dirname, repos_url)

    test.globs['import_test_package'] = import_test_package

    def create_tempdir():
        dirname = tempfile.mkdtemp('_tmpDir', 'svnhelper_')
        virtualenv = os.path.join(os.path.dirname(__file__), 'virtualenv')
        sh(sys.executable, virtualenv, dirname)[1]
        sys.executable = os.path.join(dirname, 'bin', 'python')
        test.globs['__test_dirs'].append(dirname)
        return dirname

    test.globs['create_tempdir'] = create_tempdir

def tearDownRepository(test):
    for dirname in test.globs['__test_dirs']:
        shutil.rmtree(dirname)
    sys.executable = test.globs['__executable']


