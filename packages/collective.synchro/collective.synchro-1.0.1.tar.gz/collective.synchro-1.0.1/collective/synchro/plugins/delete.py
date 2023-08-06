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

__doc__ = """ delete event """

from zope.interface import implements



from collective.synchro.interfaces.plugin import IDeleteExporter
from collective.synchro.interfaces.plugin import IDeleteImporter
from collective.synchro.data import DeletePluginData
from collective.synchro import config

class PluginExporter(object):
    """
    unit class to export data
    """
    implements(IDeleteExporter)

    def __init__(self, context):
        self.context = context

    def exportData(self):
        """
        export an IPluginData
        """
        return DeletePluginData(self.context.getId())



class PluginImporter(object):

    implements(IDeleteImporter)

    def __init__(self, data):
        self.data = data

    def importData(self, context):
        """
        import an IPluginData
        """
        if self.data.getData() in context.objectIds():
            config.logger.info('delete %s in %s' % (self.data.getData(),
                                    '/'.join(context.getPhysicalPath())))
            context.manage_delObjects([self.data.getData(),])






