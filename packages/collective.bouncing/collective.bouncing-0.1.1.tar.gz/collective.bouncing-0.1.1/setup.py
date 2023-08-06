from setuptools import setup, find_packages
import sys, os

version = '0.1.1'

setup(name='collective.bouncing',
      version=version,
      description="Mailinglist-integration with collective.singing.",
      long_description=open("README.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Malthe Borch',
      author_email='mborch@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'monkey',
          'collective.singing',
          'collective.dancing',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
