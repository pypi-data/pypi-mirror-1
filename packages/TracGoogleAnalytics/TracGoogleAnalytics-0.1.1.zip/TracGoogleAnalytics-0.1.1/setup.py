#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: setup.py 72 2008-02-23 15:38:17Z s0undt3ch $
# =============================================================================
#             $URL: http://devnull.ufsoft.org/svn/TracGoogleAnalytics/tags/0.1.1/setup.py $
# $LastChangedDate: 2008-02-23 15:38:17 +0000 (Sat, 23 Feb 2008) $
#             $Rev: 72 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

import re
from setuptools import setup

setup(name="TracGoogleAnalytics",
      version='0.1.1',
      author="Pedro Algarvio",
      author_email='ufs@ufsoft.org',
      description='Trac plugin to enable your trac environment to be logged by Google Analytics',
      long_description=re.sub(r'(\.\.[\s]*[\w]*::[\s]*[\w+]*\n)+', r'::\n', open('README.txt').read()),
      packages=['tracgoogleanalytics'],
      package_data = {'tracgoogleanalytics': ['templates/*.html']},
      include_package_data = True,
      keywords = "trac plugin google analytics",
      entry_points = {
        'trac.plugins': [ 'tracgoogleanalytics = tracgoogleanalytics' ]
      },
      classifiers = [
          'Framework :: Trac',
      ]
)
