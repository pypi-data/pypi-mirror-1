from setuptools import setup, find_packages
import sys, os

version = '1.0a1'

setup(name='vice.outbound',
      version=version,
      description="Zope library for outbound syndication.",
      long_description="""\
vice.outbound is a library for syndicating web feeds (rss, atom, etc). It
uses the Zope Component Architecture.
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='syndication atom rdf rss zope feeds',
      author='Derek Richardson',
      author_email='syndication@derekrichardson.net',
      url='http://www.openplans.org/projects/vice/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['vice'],
      include_package_data=True,
      zip_safe=False,
# keep synced with lists of fake zope2 eggs in buildout
      install_requires=[
          # -*- Extra requirements: -*-
          'setuptools',
          'collective.uuid',
          'feedparser',
          #  zope3 here down
          'ZODB3',
          'ZConfig',
          'zdaemon',
          'zope.publisher',
          'zope.traversing',
          'zope.app.wsgi>=3.4.0',
          'zope.app.appsetup',
          'zope.app.zcmlfiles',
          # The following packages aren't needed from the
          # beginning, but end up being used in most apps
          'zope.annotation',
          'zope.copypastemove',
          'zope.formlib',
          'zope.i18n',
          'zope.app.authentication',
          'zope.app.session',
          'zope.app.intid',
          'zope.app.keyreference',
          'zope.app.catalog',
          # The following packages are needed for functional
          # tests only
          'zope.testing',
          'zope.app.testing',
          'zope.app.securitypolicy',
          # vice-specific
          'zope.app.form',
          'zope.viewlet',
          'zope.securitypolicy',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
