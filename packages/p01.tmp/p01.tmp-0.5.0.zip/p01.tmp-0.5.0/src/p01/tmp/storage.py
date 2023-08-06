##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import md5
import random
import time
import os
import datetime
import pytz
import transaction
import uuid
from transaction.interfaces import IDataManager

import zope.interface
from zope.schema.fieldproperty import FieldProperty

from p01.tmp import interfaces
import p01.tmp.file


class TMPStorage(object):
    """Temporary file storage."""

    zope.interface.implements(interfaces.ITMPStorage)

    path = FieldProperty(interfaces.ITMPStorage['path'])

    def __init__(self, path):
        if not os.path.exists(path):
            os.mkdir(path)
        self.path = os.path.abspath(path)

    def generateNewTMPFilePath(self):
        """Generate a new unique unused tmp file path."""
        tz = pytz.UTC
        while True:
            #there might be a race condition around this
            #but doing this right needs quite a bit of infrastructure
            #(that also depends on the platform)
            #that would contain also some locking on the file system
            path = os.path.join(self.path, str(uuid.uuid1()))
            if not os.path.exists(path):
                break
        return path

    def getTMPFile(self):
        """Returns a TMPFile

        The file get observed by a transaction manager and will get removed
        at the end of our transaction if the file didn't get moved to a storage.
        """
        path = self.generateNewTMPFilePath()
        path = os.path.abspath(path)
        return p01.tmp.file.TMPFile(path)
