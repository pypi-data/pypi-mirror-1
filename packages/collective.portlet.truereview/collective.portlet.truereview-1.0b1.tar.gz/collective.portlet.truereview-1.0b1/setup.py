from setuptools import setup, find_packages
import os

version = '1.0b1'

setup(name='collective.portlet.truereview',
      version=version,
      description="A review portlet that takes review permissions into account",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone portlet review',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/collective.portlet.truereview',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone>=3.3rc1',
          'plone.indexer',
          'plone.app.portlets',
          'collective.autopermission',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
