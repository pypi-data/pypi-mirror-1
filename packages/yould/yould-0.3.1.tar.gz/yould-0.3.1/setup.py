#!/usr/bin/python

# Copyright 2007 Yannick Gingras <ygingras@ygingras.net>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
# MA 02110-1301 USA

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
    name='yould',
    version="0.3.1",
    description="a word generator",
    author="Yannick Gingras",
    author_email="ygingras@ygingras.net",
    url="http://ygingras.net/b/tag/yould",
    license='GPL v2 or later',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    package_data = {
       '': ['*.yould'],
    },
    entry_points={
      'console_scripts': ["yould = yould.generate:main",
                          "yould-train = yould.train:main"],
    },
)
