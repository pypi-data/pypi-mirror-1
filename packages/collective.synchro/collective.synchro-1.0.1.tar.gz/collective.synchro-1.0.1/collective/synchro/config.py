# -*- coding: utf-8 -*-
## Copyright (C) 2008 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


# CMF imports
import logging
from Products.CMFCore import permissions

GLOBALS = globals()
PROJECTNAME = "collective.synchro"
TOOLNAME = 'portal_synchronisation'
ICON = '++resource++portal_synchro.png'

logger = logging.getLogger(PROJECTNAME)
#logger.error('Error during wrapUser %s' % sys.exc_info())

## for fss
HAS_FSS_27 = False
try:
    from iw.fss import FileSystemStorage
    HAS_FSS_27 = True
except ImportError,e:
    HAS_FSS_27 = False
HAS_FSS_26 = False
try:
    from Products.FileSystemStorage import FileSystemStorage
    HAS_FSS_26 = True
except ImportError,e:
    HAS_FSS_26 = False

HAS_FSS = HAS_FSS_27 or HAS_FSS_26


HAS_PLONE3 = False
try:
    from Products.CMFPlone.migrations import v3_0
    HAS_PLONE3 = True
except ImportError,e:
    HAS_PLONE3 = False

HAS_PLONE25 = False
try:
    from Products.CMFPlone.migrations import v2_5
    HAS_PLONE25 = True
except ImportError,e:
    HAS_PLONE25 = False

if HAS_PLONE3 is False and HAS_PLONE25 is False:
    raise Exception('Please install a good version of plone')

if HAS_PLONE25 and HAS_PLONE3:
    HAS_PLONE25 = False



## for lingua plone
try:
    from Products.PloneLanguageTool import LanguageTool
    HAS_LANGUAGE_TOOL = True
except:
    HAS_LANGUAGE_TOOL = False

## lingua plone
try:
    from Products.LinguaPlone.public import *
    HAS_LINGUA_PLONE = True
except:
    HAS_LINGUA_PLONE = False

