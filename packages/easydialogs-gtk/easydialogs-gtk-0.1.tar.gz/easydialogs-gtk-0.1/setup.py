#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='easydialogs-gtk',
      version='0.1',
      install_requires=["PyGTK>=2.0"],
      packages = find_packages(),
      package_data = {'':['EasyDialogs/__init__.py'],
                      '':['*.txt']
                      },
      description='EasyDialogs for Linux',
      long_description='The EasyDialogs module includes classes and functions for working with simple message and prompt dialogs, well as stock dialogs for querying the user for file or directory names.',
      author='Lukas Sedenka',
      author_email='sedenkal@gmail.com',
      license='http://www.opensource.org/licenses/bsd-license.php',
      url='http://code.google.com/p/easydialogs-gtk/',
      keywords = "dialog gtk pygtk python",
      platforms = ["any"],


     )
