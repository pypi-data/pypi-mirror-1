# -*- coding: utf-8 -*-
from setuptools import Command
from svnhelper.script import main
import logging
import shutil
import sys
import os

logging.root.setLevel(logging.INFO)

class svn(Command):
    """the entry point
    """

    description = "svn helper"
    user_options = [
            ("import=", "i",
             "initial import"),
            ("develop=", "d",
             "checkout an svn module in parent directory"
             "and run python setup.py develop on it"),
            ("clean", "c",
             "clean package"),
            ("verbose", "v",
             "more print"),
            ]

    def initialize_options(self):
        """init options
        """
        setattr(self,'import','')
        self.develop = ''
        self.clean = False

    def finalize_options(self):
        """init options
        """
        self.import_url = getattr(self, 'import', '')

    def run(self):
        """runner
        """
        main(commande=True)


class clean(Command):
    description = "svn clean"
    user_options = []
    def initialize_options(self):pass
    def finalize_options(self):pass
    def run(self):
        sys.argv = [sys.argv[0], 'svn', '-c']
        main(commande=True)


class svnimport(Command):
    description = "svn import"
    user_options = []
    def initialize_options(self):pass
    def finalize_options(self):pass
    def run(self):
        url = raw_input('Enter a svn url:\n')
        if url:
            sys.argv = [sys.argv[0], 'svn', '--import=%s' % url]
            main(commande=True)

