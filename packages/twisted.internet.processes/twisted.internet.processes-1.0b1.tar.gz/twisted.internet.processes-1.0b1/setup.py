from setuptools import setup, find_packages
import os

version = '1.0b1'

setup(name='twisted.internet.processes',
      version=version,
      description="An implementation of deferToProcess using the "
                  "multiprocessing package.",
      long_description=open(os.path.join("docs", "README")).read() + 
											 "\n\nLicense\n=======\n" +
                       open(os.path.join("docs", "LICENSE")).read() + "\n\n" +
											 open(os.path.join("docs", "HISTORY")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Twisted",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing", 
        ],
      keywords='twisted multiprocessing deferToProcess',
      author='Benjamin Liles (Texas A&M University)',
      author_email='bliles@library.tamu.edu',
      url='http://code.google.com/p/meercat',
      license='Apache 2.0',
      packages=find_packages(exclude=['tests']),
      namespace_packages=['twisted', 'twisted.internet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Twisted',
          'multiprocessing<2.6.2.1'
      ],)
