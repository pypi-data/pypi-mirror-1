#!/usr/bin/env python
# vi:si:et:sw=2:sts=2:ts=2
# encoding: utf-8
from setuptools import setup, find_packages

setup(
  name="pysubtitles",
  version="0.2",
  description="Python Subtitle Class",
  author="j",
  author_email="j@oil21.org",
  url="http://oil21.org/~j/code/pysubtitles",
  download_url="http://oil21.org/~j/code/pysubtitles/download",
  license="GPLv3",
  packages=find_packages(),
  zip_safe=False,
  install_requires=[
        'chardet',
  ],
  keywords = [
  ],
  classifiers = [
      'Development Status :: 4 - Beta',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'License :: OSI Approved :: GNU General Public License (GPL)',
  ],
  )

