#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: setup.py 57 2008-02-23 00:12:45Z s0undt3ch $
# =============================================================================
#             $URL: http://devnull.ufsoft.org/svn/TracAdsPanel/branches/0.1.x/setup.py $
# $LastChangedDate: 2008-02-23 00:12:45 +0000 (Sat, 23 Feb 2008) $
#             $Rev: 57 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

import re
from setuptools import setup, find_packages

setup(name="TracAdsPanel",
      version='0.1.1',
      author="Pedro Algarvio",
      author_email='ufs@ufsoft.org',
      description='Trac plugin designed to display ads on your Trac environment',
      long_description=re.sub(r'(\.\.[\s]*[\w]*::[\s]*[\w+]*\n)+', r'::\n', open('README.txt').read()),
      packages=find_packages(),
      entry_points = {
        'trac.plugins': [ 'adspannel = adspanel' ]
      }
)
