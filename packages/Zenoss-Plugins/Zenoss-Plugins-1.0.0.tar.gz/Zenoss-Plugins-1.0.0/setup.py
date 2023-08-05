#!/usr/bin/env python

###############################################################################
#
#   Copyright (c) 2006 Zenoss, Inc. all rights reserved.
#
#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License.
#
###############################################################################


import os

DIR = os.path.dirname(os.path.abspath(__file__))
DESCRIPTION_DOC = 'README.txt'

def get_description():
    '''return the description information'''

    return open(os.path.join(DIR, DESCRIPTION_DOC)).read()

from setuptools import setup


VERSION = "1.0.0"

scripts = ['scripts/zenplugin.py']

setup(name = "Zenoss-Plugins",
      version = VERSION,
      description = "Zenoss-Plugins collect information about your workstation and report them on the command line.",
      author = "Christopher Blunck",
      author_email = "chris@swcomplete.com",
      package_data = {
        '' : ['*.txt']
        },
      license = "GPL",
      long_description = get_description(),
      keywords= "network management",
      url = "http://www.zenoss.com",
      packages = ['zenoss', 'zenoss.plugins'],
      scripts = scripts,
      )
    
    
