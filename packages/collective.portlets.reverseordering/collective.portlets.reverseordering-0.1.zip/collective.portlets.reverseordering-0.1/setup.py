from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.portlets.reverseordering',
      version=version,
      description="Reverse the acquisition ordering, having the global portlets on top and local at the bottom.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone',
      author='Helge Tesdal',
      author_email='tesdal@jarn.com',
      url='',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlets'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.portlets >=1.1, <1.2',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
