#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import sys

class CooprInstaller(Installer):

    def __init__(self):
        Installer.__init__(self)
        self.default_dirname='coopr'
        self.config_file='https://software.sandia.gov/svn/public/coopr/vpy/installer.ini'

    def modify_parser(self, parser):
        Installer.modify_parser(self, parser)

        parser.add_option('--forum',
            help='Use one or more packages from the Coopr Forum.  Multiple packages are specified with a comma-separated list.',
            action='store',
            dest='forum',
            default='')

    def get_other_packages(self, options):
        for pkg in options.forum.split(','):
            if pkg is '':
                continue
            if sys.version_info < (2,6,4):
                self.add_repository(pkg, root='http://coopr-forum.googlecode.com/svn/'+pkg, dev=True, username=os.environ.get('GOOGLECODE_USERNAME',None))
            else:
                self.add_repository(pkg, root='https://coopr-forum.googlecode.com/svn/'+pkg, dev=True, username=os.environ.get('GOOGLECODE_USERNAME',None))


def create_installer():
    return CooprInstaller()
