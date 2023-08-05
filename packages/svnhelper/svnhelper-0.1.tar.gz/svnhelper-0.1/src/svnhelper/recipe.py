# -*- coding: utf-8 -*-
from svnhelper.core import get_package_url
from svnhelper.core import helper
import os

class Develop:

    def __init__(self, buildout, options, name):
        self.buildout, self.options, self.name = buildout, options, name

    def install(self):
        pwd = os.getcwd()

        develop = self.options.get('develop')
        packages = develop.split('\n')

        links = self.options.get('find-links')
        links = links.split('\n')

        if not links:
            print 'No find-links provided. Skip svnhelper:Develop'
            return

        for package in packages:
            url = get_package_url(packages, links)
            if not url:
                raise SystemError('No find-links')
            else:
                helper.develop_from(pwd, url)

        os.chdir(pwd)

        self.buildout['buildout']['develop'] = develop
        installed_develop_eggs = buildout._develop()
        self._update_installed(installed_develop_eggs=installed_develop_eggs)

        return ()


    udpate = install

