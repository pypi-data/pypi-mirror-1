from setuptools import setup, find_packages
import os

version = '0.9b'

setup(name='msp2plone',
      version=version,
      description="An M$ Project XML to Plone 'eXtreme Management' importer.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Stefan Eletzhofer',
      author_email='stefan.eletzhofer@inquant.de',
      url='https://msp2plone.googlecode.com/svn/tags/0.9b',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['inquant'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'lxml',
          'wsapi4plone.client',
      ],
      entry_points={
          'console_scripts': [
              'msp2plone = inquant.msp2plone:msp2plone',
              ]
          }
      )
