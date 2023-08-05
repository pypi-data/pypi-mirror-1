#!/usr/bin/env python

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup,find_packages

def main():
  long_description = """
Tools for building large web applications using Clearsilver:

  odb.py - object to relational database mapping
         - with connectors for Sqlite, MYSQL, and Postgres

  CSPage.py - web application framework
  
  trans - transparent internationalization system
"""

  setup(name='pyclearsilver',
        version='1.0',
        packages=find_packages(),

        install_requires = ["clearsilver>=0.10.1"],

        author = "Python Clearsilver developers",
        author_email = "jeske@willowmail.com,hassan@willowmail.com",
        description = "Python modules for building web applications with Clearsilver",
        download_url = "http://www.willowmail.com/clearsilver/pyclearsilver-1.0.tar.gz",
        long_description = long_description,
        license = "Apache",

        platforms = "ALL",
        classifiers = [
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          ]
      )


if __name__ == "__main__":
    main()
