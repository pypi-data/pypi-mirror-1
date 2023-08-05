# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: admin.py 52 2008-02-22 18:08:58Z s0undt3ch $
# =============================================================================
#             $URL: http://devnull.ufsoft.org/svn/TracGoogleAnalytics/trunk/tracgoogleanalytics/admin.py $
# $LastChangedDate: 2008-02-22 18:08:58 +0000 (Fri, 22 Feb 2008) $
#             $Rev: 52 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

from trac.core import *
from trac.web.chrome import ITemplateProvider
from trac.admin import IAdminPanelProvider
from trac.config import Option, BoolOption, _TRUE_VALUES
from pkg_resources import resource_filename

class TracGoogleAnalyticsAdminPanel(Component):
    config = None
    implements(ITemplateProvider, IAdminPanelProvider)

    def __init__(self):
        self.options = {}

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        """Return the absolute path of a directory containing additional
        static resources (such as images, style sheets, etc).
        """
        return []

    def get_templates_dirs(self):
        """Return the absolute path of the directory containing the provided
        Genshi templates.
        """
        return [resource_filename(__name__, 'templates')]

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        if req.perm.has_permission('TRAC_ADMIN'):
            yield ('google_analytics', 'Google Analytics', 'config',
                   'Configuration')

    def render_admin_panel(self, req, cat, page, path_info):
        if req.method.lower() == 'post':
            self.config.set('google_analytics', 'uid',
                            req.args.get('uid'))
            self.config.set('google_analytics', 'admin_logging',
                            req.args.get('admin_logging') in _TRUE_VALUES)
            self.config.set('google_analytics', 'outbound_link_tracking',
                            req.args.get('outbound_link_tracking') in \
                            _TRUE_VALUES)
            self.config.set('google_analytics', 'google_external_path',
                            req.args.get('google_external_path'))
            self.config.set('google_analytics', 'extensions',
                            req.args.get('extensions'))
            self.config.set('google_analytics', 'tracking_domain_name',
                            req.args.get('tracking_domain_name'))
            self.config.save()
        self.update_config()
        return 'admin_google_analytics.html', {'ga': self.options}

    def update_config(self):
        for option in [option for option in Option.registry.values()
                       if option.section == 'google_analytics']:
            value = ''
            if option.name in ('admin_logging', 'outbound_link_tracking'):
                value = self.config.getbool('google_analytics', option.name,
                                            option.default)
                option.value = value
            else:
                value = self.config.get('google_analytics', option.name,
                                        option.default)
                option.value = value
            self.options[option.name] = option
