# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: web_ui.py 52 2008-02-22 18:08:58Z s0undt3ch $
# =============================================================================
#             $URL: http://devnull.ufsoft.org/svn/TracGoogleAnalytics/trunk/tracgoogleanalytics/web_ui.py $
# $LastChangedDate: 2008-02-22 18:08:58 +0000 (Fri, 22 Feb 2008) $
#             $Rev: 52 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

from trac.core import *
from trac.web.api import ITemplateStreamFilter
from trac.config import Option
from genshi.filters.transform import Transformer
from genshi.template.loader import TemplateLoader
from pkg_resources import resource_filename


class GoogleAnalyticsStreamFilter(Component):
    config = None
    implements(ITemplateStreamFilter)

    # ITemplateStreamFilter method
    def filter_stream(self, req, method, filename, stream, data):
        if req.path_info.startswith('/admin'):
            return stream
        options = self.get_options()
        if not options['uid']:
            return stream
        if ('TRAC_ADMIN' in req.perm) and (not options['admin_logging']):
            return stream
        loader = TemplateLoader(resource_filename(__name__, 'templates'))
        template = loader.load('google_analytics.html')
        data = template.generate(
            admin= 'TRAC_ADMIN' in req.perm,
            opt=options,
            base_url='http:\/\/%s' % req.environ['HTTP_HOST'])
        return stream | Transformer('body').append(data)

    def get_options(self):
        options = {}
        for option in [option for option in Option.registry.values()
                       if option.section == 'google_analytics']:
            value = ''
            if option.name in ('admin_logging', 'outbound_link_tracking'):
                value = self.config.getbool('google_analytics', option.name,
                                            option.default)
                option.value = value
            elif option.name == 'extensions':
                value = self.config.get('google_analytics', option.name,
                                        option.default)
                option.value = '|'.join(val.strip() for val in value.split(','))
            else:
                value = self.config.get('google_analytics', option.name,
                                        option.default)
                option.value = value
            options[option.name] = option.value
        return options

