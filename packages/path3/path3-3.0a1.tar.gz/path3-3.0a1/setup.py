# -*- coding: UTF-8 -*-
##############################################################################
#
# Copyright (c) 2009 Marc-J. Tegethoff
# All Rights Reserved.
#
##############################################################################
"""Setup

$Id: setup.py 1340 2009-07-17 01:13:26Z teg $
"""
    
from distutils.core import setup

setup(
      name='path3',
      version='3.0a1',
      description='Object for working with files and directories',
      long_description="""path3 provides a class (path) for working with files and directories. 
      Less typing than os.path, more fun, a few new tricks.""",
      keywords = "path manipulation",
      classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',],
      author='Jason Orendorff',
      author_email='jason at jorendorff com',
      maintainer="Marc-J. Tegethoff",
      maintainer_email="marc@tegethoff.org",
      url='https://sourceforge.net/projects/python-path3',
      packages=['path3'],
      package_dir = {'': 'src'}
      )

