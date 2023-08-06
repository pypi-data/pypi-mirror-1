from setuptools import setup, find_packages
import sys, os

version = '0.7.1'

f = open('README.txt')
readme = "".join(f.readlines())
f.close()

setup(name='Products.listen',
      version=version,
      description="listen is a mailing list product for Plone",
      long_description=readme,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Robert Marianski',
      author_email='rmarianski at openplans.org',
      url='http://oss.openplans.org/listen',
      license='GPL',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
