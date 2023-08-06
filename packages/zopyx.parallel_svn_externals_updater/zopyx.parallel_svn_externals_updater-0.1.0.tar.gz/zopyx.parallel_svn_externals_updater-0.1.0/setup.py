from setuptools import setup, find_packages
import os

version = '0.1.0'

setup(name='zopyx.parallel_svn_externals_updater',
      version=version,
      description="Script for parallel update of  svn:externals within a SVN checkout",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Subversion SVN externals ',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://svn.plone.org/svn/collective/zopyx.parallel_svn_externals_updater',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zopyx'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'processing',
          # -*- Extra requirements: -*-
      ],
      entry_points={'console_scripts': ['svn-externals-update= zopyx.parallel_svn_externals_updater.cli:main',]},
      )
