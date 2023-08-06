#!/usr/bin/env python

# Copyright 2009-2011 Olemis Lang <olemis at gmail.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from __init__ import __doc__ as DESC

versions = [
    (1, 0, 0),
    (1, 1, 0),
    (1, 2, 0),
    (1, 2, 1),
    (1, 2, 2),
    (1, 2, 3),
    (1, 3, 1),
    (1, 3, 2),
    (1, 3, 3),
    (1, 3, 4),
    ]
    
latest = '.'.join(str(x) for x in versions[-1])

status = {
            'planning' :  "Development Status :: 1 - Planning",
            'pre-alpha' : "Development Status :: 2 - Pre-Alpha",
            'alpha' :     "Development Status :: 3 - Alpha",
            'beta' :      "Development Status :: 4 - Beta",
            'stable' :    "Development Status :: 5 - Production/Stable",
            'mature' :    "Development Status :: 6 - Mature",
            'inactive' :  "Development Status :: 7 - Inactive"
         }
dev_status = status["alpha"]

cats = [
    dev_status,
    "Environment :: Plugins",
    "Environment :: Web Environment",
    "Framework :: Trac",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "Intended Audience :: Other Audience",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Natural Language :: English",
    "Natural Language :: Spanish",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python",
    "Topic :: Database",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
    "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    "Topic :: Internet :: WWW/HTTP :: WSGI",
    "Topic :: Software Development :: Bug Tracking",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Software Development :: User Interfaces",
    "Topic :: Software Development :: Widget Sets"
    ]

# Be compatible with older versions of Python
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

# Add the change log to the package description.
chglog = None
try:
    from os.path import dirname, join
    chglog = open(join(dirname(__file__), "CHANGES"))
    DESC+= ('\n\n' + chglog.read())
finally:
    if chglog:
        chglog.close()

DIST_NM = 'TracGViz'
PKG_INFO = {'tracgviz' : ('.',                           # Package dir
                            # Package data
                            ['templates/*', 'htdocs/*', 
                      		    'messages/es/LC_MESSAGES/*', 'CHANGES', 
                              'COPYRIGHT', 'NOTICE', 'README', 'TODO'],
                          ), 
            'tracgviz.ig' : ('./ig',                     # Package dir
                            # Package data
                            ['templates/*', 'htdocs/*'],
                          ), 
            }

ENTRY_POINTS = """
               [trac.plugins]
               tracgviz = tracgviz
               """

setup(
	name=DIST_NM,
	version=latest,
	description=DESC.split('\n', 1)[0],
	author='Olemis Lang',
	author_email='olemis@gmail.com',
	maintainer='Olemis Lang',
	maintainer_email='olemis@gmail.com',
	url='https://opensvn.csie.org/traccgi/swlcu/wiki/En/Devel/%s' % (DIST_NM,),
	download_url='http://pypi.python.org/packages/2.5/%s/%s/%s-%s-py2.5.egg' % \
	                              (DIST_NM[0], DIST_NM, DIST_NM, latest,),
	requires = ['trac', 'tracrpc', 'gviz_api'],
	package_dir = dict([p, i[0]] for p, i in PKG_INFO.iteritems()),
	packages = PKG_INFO.keys(),
	package_data = dict([p, i[1]] for p, i in PKG_INFO.iteritems()),
	include_package_data=True,
	provides = ['%s (%s)' % (p, latest) for p in PKG_INFO.keys()],
	obsoletes = ['%s (>=%s.0.0, <%s)' % (p, versions[-1][0], latest) \
	              for p in PKG_INFO.keys()],
	entry_points = ENTRY_POINTS,
	classifiers = cats,
	long_description= DESC
	)
