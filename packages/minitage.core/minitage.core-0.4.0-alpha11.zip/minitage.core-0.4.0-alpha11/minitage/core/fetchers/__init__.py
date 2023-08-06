#!/usr/bin/env python

# Copyright (C) 2008, Mathieu PASQUET <kiorky@cryptelium.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

__docformat__ = 'restructuredtext en'

from minitage.core.fetchers.scm import HgFetcher, SvnFetcher, BzrFetcher
from minitage.core.fetchers.static import StaticFetcher
from minitage.core.fetchers.interfaces import IFetcherFactory, IFetcher

# vim:set et sts=4 ts=4 tw=80:
