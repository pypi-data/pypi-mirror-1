#! /usr/bin/env python
# (C) Copyright 2005 Nuxeo SAS <http://nuxeo.com>
# Author: bdelbosc@nuxeo.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
#
"""twill-record package setup

$Id: setup.py 24768 2005-08-31 14:01:05Z bdelbosc $
"""
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
#from distutils.core import setup
from twillrecord import __version__
setup(
    name="twillrecord",
    version=__version__,
    description="Twill script recorder.",
    long_description="""\
Twill script recorder
* Functional testing of web projects, and thus regression testing as well.

* Performance testing: by loading the web application and monitoring
  your servers it helps you to pinpoint bottlenecks, giving a detailed
  report of performance measurement.

* Load testing tool to expose bugs that do not surface in cursory testing,
  like volume testing or longevity testing.

* Stress testing tool to overwhelm the web application resources and test
  the application recoverability.

* Writing web agents by scripting any web repetitive task, like checking if
  a site is alive.
""",
    author="Supreet Sethi",
    author_email="supreet@phire.com",
    url="http://supreetsethi.net/",
    license='GPL',
    keywords='testing benching load performance functional monitoring',
    packages= ['twillrecord'],
    package_dir={'twillrecord': 'twillrecord'},
    scripts=['scripts/twill-record', 'scripts/tcpwatch.py'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: System :: Benchmark',
        'Topic :: System :: Monitoring',
    ],
    # setuptools specific keywords
    install_requires = [],
    zip_safe=True,
    package_data={},
    # this test suite works only on an installed version :(
    # test_suite = "funkload.tests.test_Install.test_suite",
    )
