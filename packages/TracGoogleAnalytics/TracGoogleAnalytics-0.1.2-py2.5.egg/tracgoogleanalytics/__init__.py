# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: __init__.py 110 2008-08-20 12:39:05Z s0undt3ch $
# =============================================================================
#             $URL: http://devnull.ufsoft.org/svn/TracGoogleAnalytics/trunk/tracgoogleanalytics/__init__.py $
# $LastChangedDate: 2008-08-20 13:39:05 +0100 (Wed, 20 Aug 2008) $
#             $Rev: 110 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

from trac import __version__
if [int(x.split('dev')[0]) for x in __version__.split('.')][1] < 11:
    raise ImportError("Trac < 0.11 not supported")

import admin, config, web_ui
