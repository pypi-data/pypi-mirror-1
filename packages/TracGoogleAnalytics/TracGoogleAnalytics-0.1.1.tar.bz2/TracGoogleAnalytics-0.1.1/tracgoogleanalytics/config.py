# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: config.py 50 2008-02-22 17:12:30Z s0undt3ch $
# =============================================================================
#             $URL: http://devnull.ufsoft.org/svn/TracGoogleAnalytics/trunk/tracgoogleanalytics/config.py $
# $LastChangedDate: 2008-02-22 17:12:30 +0000 (Fri, 22 Feb 2008) $
#             $Rev: 50 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

from trac.core import *
from trac.config import Option, BoolOption

class TracGoogleAnalyticsConfig(Component):
    uid = Option(
        'google_analytics', 'uid', None,
        """Google Analytics' UID.
        The UID is needed for Google Analytics to log your website stats.
        Your UID can be found by looking in the JavaScript Google Analytics
        gives you to put on your page. Look for your UID in between
        `var pageTracker = _gat._getTracker("UA-111111-11");` in the javascript.
        In this example you would put UA-11111-1 in the UID box.""")
    admin_logging = BoolOption(
        'google_analytics', 'admin_logging', False,
        """Disabling this option will prevent all logged in admins from showing
        up on your Google Analytics reports.""")
    outbound_link_tracking = BoolOption(
        'google_analytics', 'outbound_link_tracking', True,
        """Disabling this option will turn off the tracking of outbound links.
        It's recommended not to disable this option unless you're a privacy
        advocate (now why would you be using Google Analytics in the first
        place?) or it's causing some kind of weird issue.""")
    google_external_path = Option(
        'google_analytics', 'google_external_path', '/external/',
        """This will be the path shown on Google Analytics
        regarding external links. Consider the following link:
          http://trac.edgewall.org/"
        The above link will be shown as for example:
          /external/trac.edgewall.org/
        This way you will be able to track outgoing links.
        Outbound link tracking must be enabled for external links to be tracked."""
        )
    extensions = Option(
        'google_analytics', 'extensions', 'zip,tar,tar.gz,tar.bzip,egg',
        """Enter any extensions of files you would like to be tracked as a
        download. For example to track all MP3s and PDFs enter:
            mp3,pdf
        Outbound link tracking must be enabled for downloads to be tracked.""")
    tracking_domain_name = Option(
        'google_analytics', 'tracking_domain_name', None,
        """If you're tracking multiple subdomains with the same Google Analytics
        profile, like what's talked about in:
            https://www.google.com/support/googleanalytics/bin/answer.py?answer=55524
        enter your main domain here. For more info, please visit the previous link.""")
