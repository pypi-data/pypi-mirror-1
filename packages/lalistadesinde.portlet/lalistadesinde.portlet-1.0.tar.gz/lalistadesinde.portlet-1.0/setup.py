from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='lalistadesinde.portlet',
      version=version,
      description="La lista de Sinde portlet for Plone",
      long_description=open("README.txt").read() + "\n", 
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='lalistadesinde',
      author='hacktivistas',
      author_email='contacto@lalistadesinde.net',
      url='http://lalistadesinde.net',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['lalistadesinde'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],
      )
