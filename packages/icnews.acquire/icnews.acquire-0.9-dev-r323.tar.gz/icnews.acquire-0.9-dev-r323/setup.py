# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: setup.py 288 2008-06-16 14:51:52Z crocha $
#
# end: Platecom header
import os
from setuptools import setup, find_packages

source_path=os.path.join(os.path.dirname(__file__), 'icnews', 'acquire')
version=open(os.path.join(source_path, 'version.txt')).read()
long_description=open(os.path.join(source_path, 'README.txt')).read() + '\n\n'

setup(name='icnews.acquire',
      version=version,
      description="icNews.Acquire",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Inter-Cultura Consultora SRL - Ibai Sistemas SA - Eusko Ikaskuntza-Sociedad de Estudios Vascos',
      author_email='dev@inter-cultura.com',
      url='www.platecom.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['icnews'],
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
