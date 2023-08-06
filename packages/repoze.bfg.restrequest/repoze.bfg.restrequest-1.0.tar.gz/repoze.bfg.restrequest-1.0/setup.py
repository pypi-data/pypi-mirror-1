from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='repoze.bfg.restrequest',
      version=version,
      description="a REST aware Request for implementing RESTful applications with repoze.bfg",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",        
        ],
      keywords='rest restful repoze bfg web development framework request wsgi',
      author='Christian Scholz',
      author_email='cs@comlounge.net',
      url='',
      license='Repoze (BSD-like) license, http://repoze.org/license.html',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['repoze', 'repoze.bfg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'repoze.bfg',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
