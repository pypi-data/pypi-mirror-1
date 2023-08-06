from setuptools import setup, find_packages
import os

version = '1.0.3'

setup(name='collective.marshall.workflow',
      version=version,
      description="A Namespace Extension for ATXML",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Oliver Roch, Brainson New Media GmbH; Daniel Kraft, D9T GmbH',
      author_email='info@brainson.de',
      maintainer='Oliver Roch',
      maintainer_email='oliver.roch@brainson.de',
      url='http://www.brainson.de/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.marshall'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
