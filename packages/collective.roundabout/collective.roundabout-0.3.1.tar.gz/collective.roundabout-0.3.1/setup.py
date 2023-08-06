from setuptools import setup, find_packages
import os

version = '0.3.1'

setup(name='collective.roundabout',
      version=version,
      description="Add support for 360 degree panoramic photos to your Plone site.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='roundabout 360 degrees viewer',
      author='Four Digits',
      author_email='rob@fourdigits.nl',
      url='http://www.fourdigits.nl',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
