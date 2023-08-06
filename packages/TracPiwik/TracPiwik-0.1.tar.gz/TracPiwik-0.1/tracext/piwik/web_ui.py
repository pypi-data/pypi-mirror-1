# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
# Copyright © 2009 Benjamin Wohlwend <bw@piquadrat.ch>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

from genshi.filters.transform import Transformer

from trac.config import Option
from trac.core import Component, implements
from trac.web.api import ITemplateStreamFilter
from trac.web.chrome import Chrome

class PiwikStreamFilter(Component):
    """Filter a Genshi event stream prior to rendering."""
    config = env = log = None
    implements(ITemplateStreamFilter)

    # ITemplateStreamFilter method
    def filter_stream(self, req, method, filename, stream, data):
        """Return a filtered Genshi event stream, or the original unfiltered
        stream if no match.
 
        `req` is the current request object, `method` is the Genshi render
        method (xml, xhtml or text), `filename` is the filename of the template
        to be rendered, `stream` is the event stream and `data` is the data for
        the current template.

        See the Genshi documentation for more information.
        """

        if req.path_info.startswith('/admin'):
            return stream

        options = self.get_options()
        if not options.get('piwik_siteid'):
            self.log.debug('Plugin not configured, returning stream')
            return stream
        elif 'TRAC_ADMIN' in req.perm and not options['piwik_admin_logging']:
            self.log.debug("Not tracking TRAC_ADMIN's, returning stream")
            return stream
        elif req.authname and req.authname != "anonymous" \
                          and not options['piwik_authenticated_logging']:
            self.log.debug("Not tracking authenticated users, returning stream")
            return stream

        template = Chrome(self.env).load_template('piwik.html')
        data = template.generate(
            admin= 'TRAC_ADMIN' in req.perm,
            opt=options,
            base_url='http:\/\/%s' % req.environ.get('HTTP_HOST'))
        return stream | Transformer('body').append(data)

    def get_options(self):
        options = {}
        for option in [option for option in Option.registry.values()
                       if option.section == 'piwik']:
            if option.name in ('piwik_admin_logging',
                               'piwik_authenticated_logging'):
                value = self.config.getbool('piwik', option.name,
                                            option.default)
                option.value = value
            else:
                value = self.config.get('piwik', option.name,
                                        option.default)
                option.value = value
            options[option.name] = option.value
        return options

