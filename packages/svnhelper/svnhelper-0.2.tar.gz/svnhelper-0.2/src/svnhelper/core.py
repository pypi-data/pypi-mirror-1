# -*- coding: utf-8 -*-
from svnhelper.utils import get_package_from_url
from svnhelper.utils import clean_output
from svnhelper.utils import valid_scheme
from svnhelper.utils import get_binary
from svnhelper.utils import create_tree
from svnhelper.utils import get_config
from svnhelper.utils import sh
import tempfile
import logging
import shutil
import sys
import os

class Base(object):

    def svn(self, *args):
        return sh(get_binary('svn'), '--non-interactive', *args)
    svn = classmethod(svn)

    def isfile(self, url=None, infos=None):
        if not infos:
            infos = self.info(url)
        return infos.get('node kind') != 'directory'
    isfile = classmethod(isfile)

    def isdir(self, url=None, infos=None):
        if not infos:
            infos = self.info(url)
        return infos.get('node kind') == 'directory'
    isdir = classmethod(isdir)

    def ls(self, url):
        retcode, output = self.svn('ls', url)
        return [v.replace('/', '') for v in clean_output(output)]
    ls = classmethod(ls)

    def info(self, url):
        retcode, output = self.svn('info', url)
        info = {}
        for line in output.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                info[key] = value.strip()
        if 'revision' in info:
            return info
        return {}
    info = classmethod(info)

    def pget(self, prop, url):
        retcode, output = self.svn('pget', prop, url)
        return clean_output(output)
    pget = classmethod(pget)

    def pset(self, prop, value, url):
        filename = None
        actual = self.pget(prop, url)
        if type(value) in (list, tuple):
            sorted_value = value[:]
            sorted_value.sort()
            if actual and actual == sorted_value:
                return
            fd, filename = tempfile.mkstemp('_tmpProps', 'svnhelper_')
            fd = open(filename, 'wb')
            fd.write('\n'.join(list(value)))
            fd.close()
            value = '-F %s' % filename
        else:
            if actual and actual == value:
                return
            value = '"%s"' % value
        retcode, output = self.svn('pset', prop, value, url)
        if filename:
            os.remove(filename)
    pset = classmethod(pset)

    def clean_package(self, dirname, update=False, message=None):
        stdout = []

        is_versioned = helper.info(dirname) and True or False

        if update:
            logging.info('Updating package ...')
            retcode, output = helper.svn('up')
            stdout.append(output)

        logging.info('Cleaning %s ...', dirname)
        added, removed = clean_package(dirname)

        if is_versioned:

            set_ignores(dirname)

            if added and not message:
                logging.warn('Some file have been added.'
                             ' please run svn status and commit manually')
            else:
                logging.info('Commit changes ...')
                if message:
                    message = '%r' % message
                else:
                    message = '"auto cleaning package"'
                retcode, output = helper.svn('ci', '-m', message)
                stdout.append(output)

        if os.path.isfile('setup.py'):
            logging.info('Setup develop with %s...' % sys.executable)
            prefix = os.path.split(os.path.dirname(sys.executable))[0]
            retcode, output = sh(sys.executable, 'setup.py', 'develop',
                                 '--prefix=%s' % prefix)
            stdout.append(output)

        return '\n'.join(stdout)
    clean_package = classmethod(clean_package)

    def import_to(self, dirname, url, ignore_structure=False):
        """import module
        """
        url = url.strip()
        try:
            pwd = os.getcwd()
        except OSError:
            pwd = None
        dirname, package = create_tree(dirname,
                                       ignore_structure=ignore_structure)
        clean_package(dirname)
        os.chdir(dirname)
        logging.info('Import package %s at %s', package, url)
        retcode, output = self.svn('import', url,
                                    '-m', '"initial import of %s"' % package)
        shutil.rmtree(dirname)
        if pwd:
            os.chdir(pwd)
        return output
    import_to = classmethod(import_to)

    def develop_from(self, dirname, url, clean=False):
        """checkout from an url and run develop
        """
        pwd = os.getcwd()
        stdout = []
        url = url.strip()
        if not self.isdir(url):
            raise RuntimeError('Not a valid url: %s' % url)
        else:
            if self.isdir('%s/trunk' % url):
                url = '%s/trunk' % url
                logging.info('Using trunk at: %s' % url)

        package = get_package_from_url(url)
        os.chdir(dirname)
        if not os.path.isdir(package):
            logging.info('Checkout package %s ...', package)
            retcode, output = self.svn('co', url, package)
            stdout.append(output)
        else:
            logging.info('Directory %s exist. Updating ...' % package)
            retcode, output = self.svn('up', package)
            stdout.append(output)

        package_dir = os.path.join(dirname, package)
        os.chdir(package_dir)

        if clean:
            output = self.clean_package(package_dir)
            stdout.append(output)

        return '\n'.join(stdout)
    develop_from = classmethod(develop_from)

helper = Base()


def set_ignores(dirname):
    helper.pset('svn:ignore',
                ['build', 'dist', '*.egg.info', '*.pyc', '*.pyo'],
                dirname)
    for root, dirs, files in os.walk(dirname):
        for name in dirs:
            name = os.path.join(root, name)
            if '.svn' in name:
                continue
            logging.debug(' - setting svn:ignore for %s', name)
            if os.path.isfile(os.path.join(name, '__init__.py')):
                helper.pset('svn:ignore', ['*.pyc', '*.pyo'], name)
            else:
                helper.pset('svn:ignore', '*.egg-info', name)

def clean_package(dirname, exclude = ['.egg-info', '.pyc', '.pyo'],
                           include = ['.py',]):
    """
    remove files to ignore::

        >>> from svnhelper.core import clean_package
        >>> dirname, package = create_tree(test_package)
        >>> os.mkdir(os.path.join(dirname, package, 'my.testing.egg-info'))
        >>> paths = clean_package(dirname)[1]
        >>> paths.sort()
        >>> for path in paths:
        ...     print path
        /package/my.testing/my.testing.egg-info

        >>> shutil.rmtree(dirname)
    """
    removed = []
    added = []

    is_versioned = helper.info(dirname) and True or False

    def must_ignore(path):
        for n in exclude:
            if path.endswith(n):
                return n

    def remove(path):
        logging.info(' - removing %s', path)
        removed.append(path)
        if helper.info(path):
            helper.svn('rm', path)
        if os.path.isfile(path):
            os.remove(path)
        if os.path.isdir(path):
            shutil.rmtree(path)

    def must_add(path):
        for n in include:
            if path.endswith(n):
                return n

    def add(path):
        if is_versioned and not helper.info(path):
            logging.info(' - adding %s' % path)
            helper.svn('add', path)
            added.append(path)

    for root, dirs, files in os.walk(dirname):
        for name in dirs:
            if must_ignore(name) or name in ('build', 'dist'):
                remove(os.path.join(root, name))
        for filename in files:
            if must_ignore(filename):
                remove(os.path.join(root, filename))
            if must_add(filename):
                add(os.path.join(root, filename))


    return added, removed

def get_package_url(package, urls=None):
    try:
        return valid_scheme(package)
    except RuntimeError:
        pass
    logging.info('Invalid scheme. Try to retrieve package from links')
    if urls is None:
        urls = get_config('find-links')
    for url in urls:
        if url.endswith('/'):
            path = '%s%s' % (url, package)
        else:
            path = '%s/%s' % (url, package)
        logging.info('  - %s', path)
        if helper.isdir(path):
            logging.info('Got %s', path)
            return path

