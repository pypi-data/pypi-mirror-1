# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: setup.py 370 2008-10-06 16:48:00Z mromero $
#
# end: Platecom header
import os
from setuptools import setup, find_packages

source_path=os.path.join(os.path.dirname(__file__), 'icsemantic', 'core')
version=open(os.path.join(source_path, 'version.txt')).read()
long_description=open(os.path.join(source_path, 'README.txt')).read() + '\n\n'

setup(name='icsemantic.core',
      version=version,
      description="icSemantic.Core",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Topic :: Text Processing",
	"Environment :: Web Environment",
        "Framework :: Plone",
	"Development Status :: 4 - Beta",
	"Intended Audience :: Developers",
	"License :: OSI Approved :: GNU General Public License (GPL)",
	"Operating System :: OS Independent",
        "Programming Language :: Python",
	],
      keywords='icsemantic, platecom, semantic, core, plone',
      author='Inter-Cultura Consultora SRL - Ibai Sistemas SA - Eusko Ikaskuntza-Sociedad de Estudios Vascos',
      author_email='dev@inter-cultura.com',
      url='http://www.platecom.com/productos/icsemantic.core/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['icsemantic'],
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
