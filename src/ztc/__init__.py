# -*- coding: utf-8 -*-
"""Zaaktypecatalogus"""
# :copyright: (c) 2018, Maykin Media B.V.
#             All rights reserved.
# :license:   EUPL 1.2, see LICENSE for more details.

from __future__ import absolute_import, unicode_literals

import re
from collections import namedtuple

__version__ = '0.1.0'
__author__ = 'Maykin Media B.V.'
__contact__ = 'info@maykinmedia.nl'
__homepage__ = 'https://github.com/Haarlem/zaaktypecataloguscomponent/'
__docformat__ = 'restructuredtext'

# -eof meta-

version_info_t = namedtuple('version_info_t', (
    'major', 'minor', 'patch', 'releaselevel', 'serial',
))

# bumpversion can only search for {current_version}
# so we have to parse the version here.
_temp = re.match(
    r'(\d+)\.(\d+).(\d+)(.+)?', __version__).groups()
VERSION = version_info = version_info_t(
    int(_temp[0]), int(_temp[1]), int(_temp[2]), _temp[3] or '', '')
del(_temp)
del(re)
