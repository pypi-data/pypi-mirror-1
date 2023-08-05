##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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

# jsoncomponent.py
# json implementation component
# jwashin 2005-07-27
# 2005-10-09 updated to properly? handle unicode on the boundary
# 2005-09-08 updated for modularity and IResult
# 2006-05-11 allowed encoding param for reader
# 2007-02-03 made cjson the default reader/writer.  fallback with minjson.

import minjson as json
from interfaces import IJSONReader, IJSONWriter
from zope.interface import implements

try:
    import cjson
    hasCJson = True
except ImportError:
    import logging
    logger = logging.getLogger()
    logger.log(logging.INFO,"Using minjson only.  cjson is much faster and available at the cheese shop.  easy_install python-cjson")
    hasCJson = False

class JSONReader(object):
    """component implementing JSON reading"""
    implements(IJSONReader)

    def read(self,aString,encoding=None):
        if hasCJson:
            try:
                # the True parameter here tells cjson to make all strings 
                # unicode. This is a good idea here.
                return cjson.decode(aString,True)
            except cjson.DecodeError:
                pass
        # This is a fall-back position for less-well-constructed JSON
        return json.read(aString,encoding)


class JSONWriter(object):
    """component implementing JSON writing"""
    implements(IJSONWriter)

    def write(self,anObject):
        if hasCJson:
            try:
                return unicode(cjson.encode(anObject))
            except cjson.EncodeError:
                pass
        return json.write(anObject)
