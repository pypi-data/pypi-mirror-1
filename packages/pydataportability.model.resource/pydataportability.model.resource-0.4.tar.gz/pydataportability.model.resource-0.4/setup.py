from setuptools import setup, find_packages
import os

version = '0.4'

setup(name='pydataportability.model.resource',
      version=version,
      description="Model classes and interfaces for resource descriptions for pydataportability and e.g. XRD parsers",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='dataportability openweb diso xrd resources models',
      author='Christian Scholz',
      author_email='cs@comlounge.net',
      url='http://pydataportability.net',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pydataportability', 'pydataportability.model'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.interface',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
