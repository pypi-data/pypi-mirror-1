# -*- coding: utf-8 -*-
#
#  __init__.py
#  checksum
# 
#  Created by Lars Yencken on 09-11-2008.
#  Copyright 2008 Lars Yencken. All rights reserved.
#

"""
A simple app which stores checksums for files. It is particularly useful for
avoiding repeated build steps for large objects.

To do this, save a checksum of the object's dependencies after creating it
the first time. The object remains "clean" as long as the dependencies haven't
changed.
"""

# vim: ts=4 sw=4 sts=4 et tw=78:

