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
"""
common interface for a plugin dispatcher
"""

from zope.interface import Interface
from zope.interface import Attribute


class IPluginExporter(Interface):
    """
    unit class to export data
    """

    def exportData():
        """
        export an IPluginData
        """


class IPluginImporter(Interface):

    data = Attribute("IPlugin data")

    def importData(context):
        """
        import an IPluginData to the context
        """

class IPluginData(Interface):
    """
    data to import or export bay a IPluginDispatcher
    """

    def getData():
        """
        return data to be exported or imported
        """


class IFssImporter(IPluginImporter):
    """
    import fss data
    """

class IFssExporter(IPluginExporter):
    """
    export fss data
    """

class IZexpImporter(IPluginImporter):
    """
    import zexp data
    """

class IZexpExporter(IPluginExporter):
    """
    export zexp data
    """

class IDeleteImporter(IPluginImporter):
    """
    import delete data
    """

class IDeleteExporter(IPluginExporter):
    """
    export delete data
    """

class IFssPluginData(IPluginData):
    """
    specific data for fss dispatcher
    """

class IZexpPluginData(IPluginData):
    """
    specific data for  zexp dispatcher
    """

class IDeletePluginData(IPluginData):
    """
    specific data for  delete dispatcher
    """

class ILinguaPluginData(IPluginData):
    """
    specific data for lingua disptacher
    """




