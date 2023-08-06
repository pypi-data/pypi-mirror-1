#!/usr/bin/env python

# pylint: disable-msg=W0221,R0201
"""

doapfiend_gentoo
================

This plugin searches for DOAP using a Gentoo Linux pacakge name.
It takes an package name and searches all ebuilds for that pacakge
for the HOMEPAGE variables, then searches doapspace.org for DOAP
with corresponding homepage or old-homepage.

"""


import logging
import subprocess

from doapfiend.plugins.base import Plugin
from doapfiend.doaplib import print_doap
from doapfiend.plugins.homepage import do_search

__docformat__ = 'epytext'
LOG = logging.getLogger(__name__)


class GentooPlugin(Plugin):

    """Class for Gentoo Linux helper functions"""

    name = "gentoo"
    enabled = False
    enable_opt = name

    def __init__(self):
        '''Setup GentooPlugin class'''
        super(GentooPlugin, self).__init__()
            
    def add_options(self, parser, output, search):
        '''Add plugin's options to doapfiend's opt parser'''
        search.add_option('-g', '--%s' % self.name,
                action='store', 
                dest=self.enable_opt,
                help='Use a Gentoo package name to find DOAP.')
        return parser, output, search

    def search(self):
        '''
        Get DOAP given a project's homepage

        @rtype: unicode
        @return: DOAP
        '''
        cmd = ('eix',
                '-e',
                '--only-names',
                self.options.gentoo
                )
        proc = subprocess.Popen(cmd, False, stdout=subprocess.PIPE)
        pkg_name = proc.communicate()[0].strip()
        if not pkg_name:
            print "No Gentoo package found: %s" % self.options.gentoo
            return
        cmd = ('eix',
                '-e',
                '--format-compact',
                '<homepage>',
                '-c',
                pkg_name,
                )
        proc = subprocess.Popen(cmd, False, stdout=subprocess.PIPE)
        homepage = proc.communicate()[0].split()[0]
        doap = do_search(homepage)
        if not doap:
            return
        print_doap(doap)
