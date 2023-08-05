#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: setup.py 50 2008-02-22 17:12:30Z s0undt3ch $
# =============================================================================
#             $URL: http://devnull.ufsoft.org/svn/TracGoogleAnalytics/trunk/setup.py $
# $LastChangedDate: 2008-02-22 17:12:30 +0000 (Fri, 22 Feb 2008) $
#             $Rev: 50 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

import re
from setuptools import setup, find_packages

setup(name="TracGoogleAnalytics",
      version='0.1.0',
      author="Pedro Algarvio",
      author_email='ufs@ufsoft.org',
      description='Trac plugin to enable your trac environment to be logged by Google Analytics',
      long_description=re.sub(r'(\.\.[\s]*[\w]*::[\s]*[\w+]*\n)+', r'::\n', open('README.txt').read()),
      packages=find_packages(),
      entry_points = {
        'trac.plugins': [ 'tracgoogleanalytics = tracgoogleanalytics' ]
      }
)
