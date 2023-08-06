# -*- coding: utf-8 -*-

from svnhelper.core import helper
from svnhelper.core import get_package_url
from svnhelper.utils import valid_scheme
from optparse import OptionParser
import logging
import shutil
import sys
import os

parser = OptionParser()


parser.add_option("-i", "--import", dest="import_url",
                  default="", metavar="URL",
                  help="initial import")
parser.add_option("-d", "--develop", dest="develop",
                  default="", metavar="URL",
                  help="checkout an svn module in parent directory"
                       " and run python setup.py develop on it")
parser.add_option("-c", "--clean", dest="clean",
                  action="store_true",
                  default=False,
                  help="clean package")
parser.add_option("-m", "--message", dest="message",
                  default="",
                  help="commit message")
parser.add_option("-v", "--verbose", dest="verbose",
                  action="store_true",
                  default=False,
                  help="more print")
(options, args) = parser.parse_args()

parser.set_usage('''
  %(script)s -i URL
  %(script)s -d URL
  %(script)s -c''' % dict(script=sys.argv[0]))

def svnco():
    if len(sys.argv) < 2:
        print 'You must specify an url'
        return
    sys.argv = [sys.argv[0], '--develop=%s' % sys.argv[1]]
    main()


def main(commande=False):
    if commande:
        args = sys.argv[2:]
    else:
        args = sys.argv[1:]

    (options, args) = parser.parse_args(args)
    if options.import_url and options.develop:
        parser.error("you can't import and develop at same time")
        return
    logging.root.setLevel(logging.INFO)
    if options.verbose:
        logging.root.setLevel(logging.DEBUG)

    if options.develop:
        url = get_package_url(options.develop)
        if not url:
            logging.error('Can find package. abort')
            return
    elif options.import_url:
        url = options.import_url

    if options.clean:
        helper.clean_package(os.getcwd(), True, options.message)
    elif options.import_url:
        dirname = os.path.split(os.getcwd())
        basename, package = os.path.split(os.getcwd())
        try:
            url = valid_scheme(url)
        except RuntimeError, e:
            logging.error(str(e))
            return
        pwd = os.getcwd()
        output = helper.import_to(pwd, url)
        if 'Committed revision' not in output:
            logging.error('Failed to import to %s' % url)
            return
        shutil.rmtree(pwd)
        os.chdir(basename)
        helper.develop_from(basename, '%s/%s' % (options.import_url, package), clean=True)
    elif options.develop:
        helper.develop_from(os.getcwd(), url)
    else:
        parser.parse_args(['-h'])

if __name__ == '__main__':
    main()

