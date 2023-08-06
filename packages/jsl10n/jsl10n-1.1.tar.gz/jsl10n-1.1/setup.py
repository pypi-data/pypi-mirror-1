###
# Copyright 2010 Isotoma Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

import os
from setuptools import setup, find_packages

here = os.path.dirname(__file__)

version = '1.1'

setup(name='jsl10n',
      version=version,
      description="Javascript localization using Zope i18n",
      long_description=open(os.path.join(here, "README.txt")).read(),
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Framework :: Zope2",
        "Framework :: Plone",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope plone javascript l10n localization i18n internationalization',
      author='Isotoma Limited',
      author_email='richard.mitchell@isotoma.com',
      url='http://svn.plone.org/svn/collective/jsl10n',
      license='Apache 2.0',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'simplejson',
      ]
      )
