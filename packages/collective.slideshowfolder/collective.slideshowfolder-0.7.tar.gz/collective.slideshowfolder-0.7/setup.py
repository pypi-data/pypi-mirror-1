from setuptools import setup, find_packages
import os

tests_require = ['collective.testcaselayer']

version = '0.7'

setup(name='collective.slideshowfolder',
      version=version,
      description="Somtimes useful extensions to Products.slideshowfolder",
      long_description=(
          open(os.path.join(
              "collective", "slideshowfolder", "README.txt")).read()
          + "\n" + open(os.path.join(
              "collective", "slideshowfolder", "portlets.txt")).read()
          + "\n" + open(os.path.join("docs", "HISTORY.txt")).read()),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='http://pypi.python.org/pypi/collective.slideshowfolder',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.slideshowfolder',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      tests_require=tests_require,
      extras_require={'tests': tests_require},
      )
