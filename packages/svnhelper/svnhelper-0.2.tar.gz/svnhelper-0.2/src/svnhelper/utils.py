
# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser
from subprocess import Popen, PIPE, STDOUT
import tempfile
import logging
import shutil
import glob
import sys
import os

def get_binary(binary):
    for dirname in os.environ['PATH'].split(':'):
        filename = os.path.join(dirname, binary)
        if os.path.isfile(filename):
            return filename
        elif os.path.isfile(filename+'.exe'):
            return filename
    raise RuntimeError(
            'Could not find any valid binary for %s. check your PATH' % binary)

def sh(*args):
    cmd = ' '.join(list(args))
    env = os.environ.copy()
    env['LANG'] = 'C'
    env['LC_ALL'] = 'C'
    prefix = os.path.split(os.path.dirname(sys.executable))[0]
    env['PYTHONPATH'] = ':'.join(sys.path+[prefix])
    p = Popen(cmd, shell=True, env=env,
              stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    (child_stdin, child_stdout) = (p.stdin, p.stdout)
    child_stdin.close()
    os.waitpid(p.pid, 0)
    return 0, child_stdout.read()

def create_tree(source, ignore_structure=False):
    """Copy a tree from a package

    You can create trunk/tags/branches dirs too::

        >>> dirname, package = create_tree(test_package)
        >>> print package
        my.testing

        >>> ls(dirname, package)
        d branches
        d tags
        d trunk

        >>> ls(dirname, package, 'trunk')
        d .svn
        - LICENSE
        d my
        - setup.py

        >>> shutil.rmtree(dirname)

    You can ignore trunk/tags/branches structure::

        >>> dirname, package = create_tree(test_package, ignore_structure=True)
        >>> ls(dirname, package)
        d .svn
        - LICENSE
        d my
        - setup.py

        >>> shutil.rmtree(dirname)
    """
    dirname = tempfile.mkdtemp('_tmpPackage', 'svnhelper_')
    d, package = os.path.split(source)
    import_dir = os.path.join(dirname, package)
    if ignore_structure:
        dest = import_dir
    else:
        os.mkdir(import_dir)
        for d in ['tags', 'branches']:
            os.mkdir(os.path.join(import_dir, d))
        dest = os.path.join(import_dir, 'trunk')
    shutil.copytree(source, dest)
    return dirname, package

def get_package_from_url(url):
    """
    get the package name from url::

        >>> print get_package_from_url('http://server/my.testing')
        my.testing

        >>> print get_package_from_url('http://server/my.testing/trunk')
        my.testing

        >>> print get_package_from_url('http://server/my.testing/branches/b1')
        my.testing

        >>> print get_package_from_url('http://server/my.testing/tags/t1')
        my.testing

    """
    splited = url.split('/')
    for name in ['trunk', 'branches', 'tags']:
        if name in splited:
            index = splited.index(name)
            return splited[index-1]
    return splited[-1]

def clean_output(output):
    output = output.strip()
    if '\n' in output:
        if output:
            output = [f.strip() for f in output.split('\n')]
            output.sort()
            return output
    return output

def get_config(key, filenames=None):
    """
    >>> 'svn://svn.zope.org/repos/main/' in get_config('find-links')
    True
    """
    if filenames is None:
        filenames = []
    filenames.extend(glob.glob('*.cfg'))
    filenames.append(os.path.expanduser('~/.svnhelper'))
    dirname = os.path.dirname(os.path.abspath(__file__))
    filenames.append(os.path.join(dirname, 'default.cfg'))

    values = []
    for filename in filenames:
        if os.path.isfile(filename):
            parser = ConfigParser()
            parser.read([filename])
            if parser.has_option('svnhelper', key):
                items = clean_output(parser.get('svnhelper', key))
                if type(items) == type(''):
                    items = [items]
                for i in items:
                    if i not in values:
                        values.append(i)

    return values

def valid_scheme(url):
    """check url scheme::

        >>> valid_scheme('file:///tmp/repos')
        'file:///tmp/repos'

        >>> valid_scheme('fil:///tmp/rempos')
        Traceback (most recent call last):
        ...
        RuntimeError: Invalid url scheme fil:///tmp/rempos

        >>> valid_scheme('gruik')
        Traceback (most recent call last):
        ...
        RuntimeError: Invalid url scheme gruik

    """
    scheme = url.split('://')[0]
    if scheme not in ('file', 'svn', 'svn+ssh', 'http', 'https'):
        raise RuntimeError('Invalid url scheme %s' % url)
    return url

