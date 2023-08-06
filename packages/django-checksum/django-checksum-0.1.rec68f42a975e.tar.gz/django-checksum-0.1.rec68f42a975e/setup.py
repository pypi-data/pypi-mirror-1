# -*- coding: utf-8 -*-
#
#  setup.py
#  checksum
# 
#  Created by Lars Yencken on 09-11-2008.
#  Copyright 2008 Lars Yencken. All rights reserved.
#

"""
Package file for the checksum app.
"""

from setuptools import setup
import os
from os import path

def get_mercurial_id():
    revision = None
    # Is mercurial installed?
    if os.system('which hg >/dev/null 2>&1') == 0:
        revision = os.popen('hg id -i 2>/dev/null').read().strip().rstrip('+')

    return revision or 'unknown'

setup(
        name='django-checksum',
        version='0.1.r%s' % get_mercurial_id(),
        description='Django checksum app',
        long_description="""An app for managing static file dependencies using Django's ORM as a data store. This is useful when, for example, building a large resource in many stages from a variety of static dependencies, both data files and python modules. Simple methods are provided for querying whether the generated resource is up-to-date based on the checksum of its dependencies.""",
        author='Lars Yencken',
        author_email='lljy@csse.unimelb.edu.au',
        url='http://bitbucket.org/lars512/django-checksum/',
        license='GPL',
        requires=['django (>= 1.0)'],
        packages = ['checksum'],
        package_dir = {'checksum': 'src'},
    )

# vim: ts=4 sw=4 sts=4 et tw=78:

