# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
# Copyright © 2009 Benjamin Wohlwend <bw@piquadrat.ch>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from trac.admin import IAdminPanelProvider
from trac.config import Option, _TRUE_VALUES
from trac.core import Component, implements
from trac.web.chrome import add_stylesheet

class PiwikAdmin(Component):
    config = env = log = None
    options = {}
    implements(IAdminPanelProvider)

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        if req.perm.has_permission('TRAC_ADMIN'):
            yield ('piwik', 'Piwik', 'settings', 'Settings')

    def render_admin_panel(self, req, cat, page, path_info):
        add_stylesheet(req, 'piwik/tracpiwik.css')
        if req.method.lower() == 'post':
            self.config.set('piwik', 'piwik_siteid',
                            req.args.get('piwik_siteid'))
            self.config.set('piwik', 'piwik_baseurl',
                            req.args.get('piwik_baseurl'))
            self.config.set('piwik', 'piwik_admin_logging',
                            req.args.get('piwik_admin_logging') in _TRUE_VALUES)
            self.config.set('piwik', 'piwik_authenticated_logging',
                            req.args.get('piwik_authenticated_logging') in
                            _TRUE_VALUES)
            self.config.set('piwik', 'piwik_extensions',
                            req.args.get('piwik_extensions'))
            self.config.save()
        self.update_config()
        return 'piwik_admin.html', {'piwik': self.options}

    def update_config(self):
        for option in [option for option in Option.registry.values()
                       if option.section == 'piwik']:
            if option.name in ('piwik_admin_logging', 'piwik_authenticated_logging'):
                value = self.config.getbool('piwik', option.name,
                                            option.default)
                option.value = value
            else:
                value = self.config.get('piwik', option.name,
                                        option.default)
                option.value = value
            self.options[option.name] = option
