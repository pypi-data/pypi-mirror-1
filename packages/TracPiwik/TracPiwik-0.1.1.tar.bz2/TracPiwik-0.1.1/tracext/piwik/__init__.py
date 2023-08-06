# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
# Copyright © 2009 Benjamin Wohlwend <bw@piquadrat.ch>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

__version__     = '0.1.1'
__author__      = 'Benjamin Wohlwend'
__email__       = 'bw@piquadrat.ch'
__package__     = 'TracPiwik'
__license__     = 'BSD'
__url__         = 'http://bitbucket.org/piquadrat/tracpiwik/'
__summary__     = 'Trac plugin to enable your trac environment to be logged' + \
                  ' by Piwik'

import pkg_resources
from trac.config import Option, BoolOption
from trac.core import Component, implements
from trac.env import IEnvironmentSetupParticipant
from trac.web.chrome import ITemplateProvider

# ==============================================================================
# Piwik Configuration
# ==============================================================================
class PiwikConfig(Component):
    piwik_siteid = Option(
        'piwik', 'piwik_siteid', None,
        """Piwik's Site ID.""")
    piwik_baseurl = Option(
        'piwik', 'piwik_baseurl', None,
        """The base url of your Piwik installation. You can find it in the 
        <em>pkBaseURL</em> variable in the Javascript snippet from Piwik.""")
    piwik_admin_logging = BoolOption(
        'piwik', 'piwik_admin_logging', False,
        """Disabling this option will prevent all logged in admins from showing
        up on your Google Analytics reports.""")
    piwik_authenticated_logging = BoolOption(
        'piwik', 'piwik_authenticated_logging', True,
        """Disabling this option will prevent all authenticated users from
        showing up on your Google Analytics reports.""")
    piwik_extensions = Option(
        'piwik', 'piwik_extensions', '7z|aac|arc|arj|asf|asx|avi|bin|csv|' + \
                                     'doc|exe|flv|gif|gz|gzip|hqx|jar|' + \
                                     'jpe?g|js|mp(2|3|4|e?g)|mov(ie)?|msi|' + \
                                     'msp|pdf|phps|png|ppt|qtm?|ra(m|r)?|' + \
                                     'sea|sit|tar|tgz|torrent|txt|wav|wma|' + \
                                     'wmv|wpd||xls|xml|z|zip',
        """Enter any extensions of files you would like to be tracked as a
        download. For example to track all MP3s and PDFs enter:
            mp3|pdf""")



# ==============================================================================
# Piwik Resources
# ==============================================================================
class PiwikResources(Component):
    implements(ITemplateProvider)
    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        """Return the absolute path of a directory containing additional
        static resources (such as images, style sheets, etc).
        """
        yield 'piwik', pkg_resources.resource_filename(__name__,
                                                                 'htdocs')

    def get_templates_dirs(self):
        """Return the absolute path of the directory containing the provided
        Genshi templates.
        """
        yield pkg_resources.resource_filename(__name__, 'templates')

# ==============================================================================
# Upgrade Code
# ==============================================================================
#class PiwikSetup(Component):
#    env = config = log = None # make pylink happy
#    implements(IEnvironmentSetupParticipant)
#
#    def environment_created(self):
#        "Nothing to do when an environment is created"""
#
#    def environment_needs_upgrade(self, db):
#        return False
#        #return 'piwik' in self.config
#
#    def upgrade_environment(self, db):
#        # Although we're only migrating configuration stuff and there's no
#        # database queries involved, which could be done on other places,
#        # I'm placing the migration code here so that it only happens once
#        # and the admin notices that a migration was done.
#        self.log.debug('Migrating Piwik configuration')
#        for option, value in self.config.options('piwik'):
#            if self.config.has_option('piwik', option):
#                self.config.set('piwik', option, value)
#            self.config.remove('piwik', option)
#        self.config.save()
