# -*- coding: utf-8 -*-
## Copyright (C) 2006 Ingeniweb

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

""" interface use in content dispatcher """

from zope import schema
from zope.interface import Interface

from plugin import *
from queues import *
from tool import *

class ISynchroData(Interface):
    """
    marker interface for syncronize data
    """

    datas = schema.List(title= u"datas",
                        description= u"a list of IPluginData content",
                        required = True )



    def getUid():
        """ return uid of the imported object """

    def getId():
        """ return id of the imported object """

    def getImportPath():
        """ return the path where the object must be imported """


class IImportContext(Interface):
    """
    get import localisation
    """



