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


from zope.interface import Interface
from Products.CMFPlone.interfaces import IPloneBaseTool

class ISynchronisationTool(IPloneBaseTool):


    def importContent(context):
        """ import data from file queue
            @param file:file name in queue
        """




    def exportContent(synchro_data, context):
        """ export data to file queue
            @param context:the context in queue
        """

    def registerPlugin(id, klass, priority, event):
        """ register an plugin for import export data
            @param id: identifier of plugin
                   klass: class name of the plugin
                   priority : priority of the plugin
                   event : interface of event on wich this plugin is registered
        """

    def unregisterPlugin(id):
        """ unregister plugin
            @param id: identifier of plugin
        """


    def getPlugins(event):
        """ return a list order by priority """



