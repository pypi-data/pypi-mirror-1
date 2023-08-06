from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='Products.AnonPAS',
      version=version,
      description="this plugin can be used for anonymous content submission",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("Products", "AnonPAS", "README")).read() + "\n" + 
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Huub Bouma',
      author_email='info@gw20e.com',
      url='http://www.gw20e.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
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
