##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""MIME type guessing utility

This module also initializes a global utility object, thus loading the MIME
info data at the module import time (see the end of this file). 

$Id: utility.py 103666 2009-09-08 19:23:30Z nadako $
"""
import re
import os
import fnmatch

from zope.interface import implements

from z3c.sharedmimeinfo.basedir import iterDataPaths
from z3c.sharedmimeinfo.interfaces import IMIMETypesUtility
from z3c.sharedmimeinfo.magic import MagicDB
from z3c.sharedmimeinfo.mimetype import MIMEType

findBinary = re.compile('[\0-\7]').search


class MIMETypesUtility(object):
    """MIME type guessing utility"""
    
    implements(IMIMETypesUtility)

    _extensions = None
    _literals = None
    _globs = None
    _magicDB = None

    def __init__(self):
        self._extensions = {}
        self._literals = {}
        self._globs = []
        self._magicDB = MagicDB()

        for path in iterDataPaths(os.path.join('mime', 'globs')):
            self._importGlobFile(path)
        self._globs.sort(key=lambda ob:len(ob[0]), reverse=True)
        
        for path in iterDataPaths(os.path.join('mime', 'magic')):
            self._magicDB.mergeFile(path)

    def _importGlobFile(self, path):
        for line in open(path, 'r'):
            if line.startswith('#'):
                continue
            line = line[:-1]
    
            type_name, pattern = line.split(':', 1)
            mtype = MIMEType(type_name)
    
            if pattern.startswith('*.'):
                rest = pattern[2:]
                if not ('*' in rest or '[' in rest or '?' in rest):
                    self._extensions[rest] = mtype
                    continue
    
            if '*' in pattern or '[' in pattern or '?' in pattern:
                self._globs.append((pattern, mtype))
            else:
                self._literals[pattern] = mtype

    def getTypeByFileName(self, filename):
        """Return type guessed by filename"""

        if filename in self._literals:
            return self._literals[filename]
    
        lfilename = filename.lower()
        if lfilename in self._literals:
            return self._literals[lfilename]
    
        ext = filename
        while True:
            p = ext.find('.')
            if p < 0:
                break
            ext = ext[p + 1:]
            if ext in self._extensions:
                return self._extensions[ext]
    
        ext = lfilename
        while True:
            p = ext.find('.')
            if p < 0:
                break
            ext = ext[p + 1:]
            if ext in self._extensions:
                return self._extensions[ext]
    
        for (glob, mime_type) in self._globs:
            if fnmatch.fnmatch(filename, glob):
                return mime_type
            if fnmatch.fnmatch(lfilename, glob):
                return mime_type
    
        return None

    def getTypeByContents(self, file, min_priority=0, max_priority=100):
        """Return type guessed by data. Accepts file-like object"""

        return self._magicDB.match(file, min_priority, max_priority)

    def getType(self, filename=None, file=None):
        """Try to guess content type either by file name or contents or both"""

        if (filename is None) and (file is None):
            raise TypeError('Either filename or file should be provided or both of them')
        
        type = None
        
        if file:
            type = self.getTypeByContents(file, min_priority=80)

        if not type and filename:
            type = self.getTypeByFileName(filename)

        if not type and file:
            type = self.getTypeByContents(file, max_priority=80)
        
        if not type:
            type = MIMEType('application', 'octet-stream')
            if file:
                file.seek(0, 0)
                if not findBinary(file.read(32)):
                    type = MIMEType('text', 'plain')

        return type


mimeTypesUtility = MIMETypesUtility()
getType = mimeTypesUtility.getType
