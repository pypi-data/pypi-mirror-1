# -*- coding: utf-8 -*-
#
#  models.py
#  checksum
# 
#  Created by Lars Yencken on 09-11-2008.
#  Copyright 2008 Lars Yencken. All rights reserved.
#

"""
Models for the checksum app.
"""

from os import path
import types
from zlib import crc32
import datetime

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class Checksum(models.Model):
    """
    A checksum of the input files required to build part of the database.

    >>> Checksum.objects.all().delete()
    >>> Checksum.needs_update('models', [__file__])
    True
    >>> Checksum.store('models', [__file__])
    >>> Checksum.needs_update('models', [__file__])
    False
    """
    tag = models.CharField(max_length=50)
    value = models.CharField(max_length=15)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' % self.tag

    @staticmethod
    def checksum(files):
        result = 0
        for module_or_filename in files:
            # Replace module references with the file which defines them.
            if type(module_or_filename) == types.ModuleType:
                filename = module_or_filename.__file__
            else:
                filename = module_or_filename

            # Replace compiled python files with their source code.
            if (filename.endswith('.pyc') or filename.endswith('.pyo')) \
                        and path.exists(filename[:-1]):
                filename = filename[:-1]

            i_stream = open(filename, 'r')
            result = crc32(i_stream.read(), result)
            i_stream.close()

        return str(result)

    @staticmethod
    def needs_update(tag, files, dep_tags=None, delete_if_old=True):
        """
        Returns True if the database stored checksum doesn't exist or is
        different to that calculated by storing the files.

        @param tag      The tag for the stored checksum.
        @param files    Files or modules used to generate the checksum.
        @param dep_tags Tags for other objects this object depends on.
        @param delete_if_old
                        Delete any existing tag when the current tag is dirty.
        """
        if not files:
            raise ValueError, "Need at least one file to checksum"

        if dep_tags:
            latest_dep = max(Checksum.get_timestamp(t) for t in dep_tags)
        else:
            # Default to some time long in the past (1 year ago).
            latest_dep = datetime.datetime.now() - datetime.timedelta(365)

        result = Checksum.checksum(files)
        try:
            existing = Checksum.objects.get(tag=tag)
            if existing.value == result and existing.timestamp > latest_dep:
                return False
            else:
                if delete_if_old:
                    existing.delete()

        except ObjectDoesNotExist:
            pass

        return True

    @staticmethod
    def get_timestamp(tag):
        try:
            return Checksum.objects.get(tag=tag).timestamp
        except ObjectDoesNotExist:
            return datetime.datetime.now()

    @staticmethod
    def store(tag, files):
        "Store the given checksum."
        Checksum.objects.filter(tag=tag).delete()
        obj = Checksum(tag=tag, value=Checksum.checksum(files))
        obj.save()
        return

# vim: ts=4 sw=4 sts=4 et tw=78:
