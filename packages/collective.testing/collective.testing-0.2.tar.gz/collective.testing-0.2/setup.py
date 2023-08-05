from setuptools import setup, find_packages
import sys, os

version = '0.2'

f = open('README.txt')
readme = "".join(f.readlines())
f.close()

setup(name='collective.testing',
      version=version,
      description="general package for testing and debugging aids for CMF, Plone, Zope2 and Zope3",
      long_description=readme,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords="'testing debug pdb profile zope.testing'",
      author='whit',
      author_email='whit@openplans.org',
      url='https://svn.plone.org/svn/collective/collective.testing/trunk#egg=collective.testing',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
