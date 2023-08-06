#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  Copyright (C) 2010 Francis Piéraut <fpieraut@gmail.com>

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.

#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"A resource monitoring : CPU and Memory monitor webservice"

from setuptools import setup, find_packages
from resmoni import __version__

setup(name='resmonitor',
      version=__version__,
      author='Francis Pieraut',
      author_email='fpieraut@gmail.com',
      description = __doc__,
      license="AGPL v3 or later",
      packages = find_packages(),
      include_package_data=True,
      install_requires=["retro>=0.9.5"],
      entry_points={
      'console_scripts': ["usage-ws = resmoni.UsageWebService:main",
                          "usage-db = resmoni.UsageDB:main",
                          "usage-mem = resmoni.MemoryMonitor:main",
                          "usage-cpu = resmoni.CpuMonitor:main"],
      }
)
