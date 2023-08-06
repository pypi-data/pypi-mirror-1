# -*- coding: utf-8 -*-
#
#  admin.py
#  checksum
# 
#  Created by Lars Yencken on 09-11-2008.
#  Copyright 2008 Lars Yencken. All rights reserved.
#

"""
Admin interface for the checksum app.
"""

from django.contrib import admin

import models

class ChecksumAdmin(admin.ModelAdmin):
    list_display = ('tag', 'value')

admin.site.register(models.Checksum, ChecksumAdmin)

# vim: ts=4 sw=4 sts=4 et tw=78:
