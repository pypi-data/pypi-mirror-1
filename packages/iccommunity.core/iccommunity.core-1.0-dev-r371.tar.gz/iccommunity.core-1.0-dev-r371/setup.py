# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: setup.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
import os
from setuptools import setup, find_packages

source_path=os.path.join(os.path.dirname(__file__), 'iccommunity', 'core')
version=open(os.path.join(source_path, 'version.txt')).read()
long_description=open(os.path.join(source_path, 'README.txt')).read() + '\n\n'

setup(name='iccommunity.core',
      version=version,
      description="icCommunity.Core",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
	"Topic :: Communications",
	"Environment :: Web Environment",
        "Framework :: Plone",
	"Development Status :: 4 - Beta",
	"Intended Audience :: Developers",
	"License :: OSI Approved :: GNU General Public License (GPL)",
	"Operating System :: OS Independent",
        "Programming Language :: Python",
        ],
      keywords='iccommunity, platecom, community, core, plone',
      author='Inter-Cultura Consultora SRL - Ibai Sistemas SA - Eusko Ikaskuntza-Sociedad de Estudios Vascos',
      author_email='dev@inter-cultura.com',
      url='http://www.platecom.com/productos/iccommunity.core/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['iccommunity'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
