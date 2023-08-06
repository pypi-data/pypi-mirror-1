from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='plone.app.memberschema',
      version=version,
      description="Support for storing member data based on interfaces",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone zope pas member schema interface',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/plone.app.memberschema',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'ZODB3',
          'zope.schema',
          'zope.dottedname',
          'zope.i18nmessageid',
          'z3c.form',
          'plone.z3cform',
          'plone.memoize',
          'plone.autoform',
          'plone.namedfile',
          'plone.formwidget.namedfile',
          'Plone',
          'Products.PlonePAS',
          'Products.PluggableAuthService',
          'Products.statusmessages',
          'Products.CMFCore',
      ],
      entry_points="""
      """,
      )
