from setuptools import setup, find_packages
import os

version = '1.0b2'

setup(name='collective.groupdashboard',
      version=version,
      description="Assign portlets to users' dashboards on a per-group basis",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone group portlet dashboard',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/collective.groupdashboard',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.portlets',
          'collective.autopermission',
          'five.grok',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
