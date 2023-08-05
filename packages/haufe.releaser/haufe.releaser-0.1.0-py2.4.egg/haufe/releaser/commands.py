# -*- coding: utf-8 -*-

import sys
import os
import xmlrpclib
import base64
import getpass
from setuptools import Command


class ReleaseError(Exception):
    """ Generic error """
    pass


class local_upload(Command):
    """Releaser"""

    description = "Upload distribution to an Python index server (haufe.eggserver)"
    user_options = [('eggserver=', 'e', 'URL of haufe.eggserver instance'),
                   ]
    eggserver = 'http://localhost:8080/egg'

    def initialize_options(self):
        """ init options """
        pass

    def finalize_options(self):
        """finalize options"""
        pass

    def run(self):
        """ Upload packages to some index server through XML-RPC"""

        print 
        print '*'*80
        print 'Uploading of packages to a local haufe.eggserver instance (%s)' % self.eggserver

        package = self.distribution.packages[-1]
        srv = xmlrpclib.Server(self.eggserver)

        for dist, dummy, package_filename in self.distribution.dist_files:
            package_data = base64.encodestring(open(package_filename, 'rb').read())
            print 'Uploading %s to %s' % (package_filename, self.eggserver)
            try:
                srv.handle_upload(package, 
                                  os.path.basename(package_filename), 
                                  package_data,
                                  getpass.getuser())
            except Exception, e:
                raise ReleaseError(e)
            print 'Done'

