from setuptools import setup, find_packages
import os

version = '1.2'

setup(name='pyjon.descriptors',
      version=version,
      description="Provides a system of descriptors to read files and return objects",
      long_description=open("README.txt").read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Florent Aide, Jerome Collette, Jonathan Schemoul',
      author_email='florent.aide@gmail.com, collette.jerome@gmail.com, jonathan.schemoul@gmail.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pyjon'],
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
