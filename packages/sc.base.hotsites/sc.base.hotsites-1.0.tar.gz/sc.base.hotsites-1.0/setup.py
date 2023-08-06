# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = open(os.path.join("sc", "base", "hotsites", "version.txt")).read().strip()

setup(name='sc.base.hotsites',
      version=version,
      description="",
      long_description=open(os.path.join("sc", "base", "hotsites", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Simples Consultoria',
      author_email='products@simplesconsultoria.com.br',
      url='http://www.simplesconsultoria.com.br/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['sc', 'sc.base'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'p4a.subtyper',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [distutils.setup_keywords]
      paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
      paster_plugins.txt = setuptools.command.egg_info:write_arg
      """,
      paster_plugins = ["ZopeSkel"],
      )
