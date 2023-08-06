from setuptools import setup, find_packages
import os

version = '1.0b1'

setup(name='collective.discussionplus',
      version=version,
      description="Augments the standard Plone discussion tool to add basic approvals workflow, and ibetter indexing of comment metadata (number of comments, who has commented?)",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone discussion commenting',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/collective.discussionplus',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone',
          'plone.indexer',
          'collective.autopermission',
          'five.grok',
          'zope.component',
          'zope.event',
          'zope.lifecycleevent',
          'zope.app.container',
          'Products.CMFCore',
          'Products.CMFDefault',
          'plone.intelligenttext',
      ],
      entry_points="""
      """,
      )
