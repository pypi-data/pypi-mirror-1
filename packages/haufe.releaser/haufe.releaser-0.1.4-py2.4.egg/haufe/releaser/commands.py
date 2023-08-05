# -*- coding: utf-8 -*-

import sys
import os
import xmlrpclib
import base64
import getpass
from setuptools import Command
from ConfigParser import ConfigParser


releaser_config = os.path.join(os.path.expanduser('~'), '.haufe.releaser.ini')


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
        if os.path.exists(releaser_config):
            CP = ConfigParser()
            CP.read(releaser_config)
            self.eggserver = CP.get('default', 'eggserver')
            print 'Found haufe.release configuration file: %s' % releaser_config
            print 'Using Egg-Server at %s' % self.eggserver

    def finalize_options(self):
        """finalize options"""
        pass

    def run(self):
        """ Upload packages to some index server through XML-RPC"""

        print 
        print '*'*80
        print 'Uploading of packages to a local haufe.eggserver instance (%s)' % self.eggserver

        package = self.distribution.get_name()
        srv = xmlrpclib.Server(self.eggserver)

        dist_files = self.distribution.dist_files
        if not dist_files:
            print 'No distribution files found - nothing to be uploaded.'

        for dist, dummy, package_filename in dist_files:
            package_data = base64.encodestring(open(package_filename, 'rb').read())
            print ' --> Uploading %s to %s' % (package_filename, self.eggserver)
            try:
                srv.handle_upload(package, 
                                  os.path.basename(package_filename), 
                                  package_data,
                                  getpass.getuser())
            except Exception, e:
                raise ReleaseError(e)
            print 'Done'
        print '-' * 80


class check_description(Command):
    """ Check the long_description for correctness """

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):

        description = self.distribution.get_long_description()
        from rest import HTML
        warnings = HTML(description)
        if warnings:
            print 'Warnings & errors'
            print '-----------------'
            for w in warnings:
                print w
        else:
            print "The 'long_description' is appearently correct restructured-text"

