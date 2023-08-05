from setuptools import setup, find_packages
import sys, os

version = '1.0b1'

setup(name='plone.openid',
      version=version,
      description="OpenID authentication support for PAS",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        ],
      keywords='PAS openid',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.openid',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      download_url='http://code.google.com/p/plone/downloads/list',
      install_requires=[
        'setuptools',
        'python-openid >= 1.2.0',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
