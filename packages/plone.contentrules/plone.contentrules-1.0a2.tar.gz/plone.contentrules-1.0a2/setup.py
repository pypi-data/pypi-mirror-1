from setuptools import setup, find_packages
import sys, os

version = '1.0a2'

setup(name='plone.contentrules',
      version=version,
      description="Plone ContentRules Engine",
      long_description="""\
plone.contentrules provides a "pure Zope 3" implementation of a a rules 
engine which allows arbitary conditions and actions to be combined into rules,
and rules to be executed dependent on events. You can think of this as 
somewhat similar to user-assembled mail filtering rules or something like
Apple's Automator. It is used by plone.app.contentrules to provide such 
functionality for Plone.
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Markus Fuhrer, Martin Aspeli',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.contentrules',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
