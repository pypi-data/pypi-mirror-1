from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.portlet.toc',
      version=version,
      description="Portlet that shows the table of contents for the current item",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone portlet toc table contents',
      author='David Jonas',
      author_email='david@b\x08v2.nl',
      url='https:..\x08\x08//svn.v2.nl/po\x08lone',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
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
      )
