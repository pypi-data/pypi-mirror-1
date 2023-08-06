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



"""
content to be dispatched
"""


from zope.interface import implements
from zope.interface import Interface
from zope.component import queryAdapter
from zope.component import queryMultiAdapter
from zope.component import adapts

from interfaces import IPluginData
from interfaces import IFssPluginData
from interfaces import IZexpPluginData
from interfaces import ILinguaPluginData
from interfaces import IDeletePluginData
from interfaces import IPluginImporter
from interfaces import IPluginExporter
from interfaces import IDeleteImporter
from interfaces import ISynchroData
from interfaces import IFssImporter
from interfaces import IZexpImporter
from interfaces import IImportContext


from Products.CMFCore.utils import getToolByName

try:
    ## plone3
    from plone.locking.interfaces import ILockable
    from plone.locking.interfaces import INonStealableLock
except:
    ## plone2.5
    from interfaces.bbb import ILockable
    from interfaces.bbb import INonStealableLock

from events import SynchroModifiedEvent as ModifiedEvent
import config

def _indexObject(toindex):

    if toindex and hasattr(toindex,'indexObject'):
        toindex.indexObject()
    if toindex and hasattr(toindex,'isPrincipiaFolderish'):
        for obj in toindex.objectValues():
            _indexObject(obj)


class PluginData(object):

    implements(IPluginData)

    def __init__(self, data = None):
        self.data=data

    def getData(self):
        return self.data

    def __len__(self):
        return len(self.data)


class FssPluginData(PluginData):
    """
    file system storage content
    """
    implements(IFssPluginData)

    def __init__(self, data = []):
        self.data = data



class ZexpPluginData(PluginData):
    """
    zexp pluggin content
    """
    implements(IZexpPluginData)


class DeletePluginData(PluginData):
    """
    delete plugin data
    """
    implements(IDeletePluginData)



class SynchroData(object):
    """
    contains all data to dispach in a remote site
    """
    implements(ISynchroData)

    def __init__(self,context, event = ModifiedEvent()):
        """
        export data from context
        """
        tool = getToolByName(context,config.TOOLNAME)
        portal = getToolByName(context,'portal_url').getPortalObject()
        self.datas=[]
        for plugin_klass in tool.getPlugins(event):
            plugin = plugin_klass(context)
            ## return an IPluginData
            data = plugin.exportData()
            if not IPluginData.providedBy(data):
                raise SynchroError("Must be an IPlugginData")
            if len(data):
                self.datas.append(data)
        portal_path = portal.getPhysicalPath()
        self.path = context.getPhysicalPath()[len(portal_path):]

        if hasattr(context.aq_base, 'UID'):
            self.uid = context.UID()
        else:
            self.uid = ''


    def __len__(self):
        """ return the number of data plugin """

        return len(self.datas)

    def getId(self):
        """ return id of exported context """

        return self.path[-1]

    def getImportPath(self):
        """ return the container path of object """

        return '/'.join(self.path[:-1])

    def getUid(self):
        """ return uid of the exported object """

        return self.uid


    def __call__(self,context):
        """
        import data in context
        """

        for data in self.datas:
            p = None
            try:
                p = IPluginImporter(data)
            except:
                raise SynchroError('can get the importer for data %s' % str(data))
            config.logger.info('call plugin importer %s' % str(p))
            ## get import context by queyring interface
            importContext = queryMultiAdapter((context,self,p), IImportContext,
                                              default = None)
            if p is not None and importContext is not None:
                p.importData(importContext())
        object = context.restrictedTraverse('/'.join(self.path), None)

        if object:
            ## reindex
            _indexObject(object)



class SynchroError(Exception):

    pass

class ZexpImportContext(object):

    implements(IImportContext)
    adapts(Interface, ISynchroData, IZexpImporter)

    def __init__(self, context, data, importer):
        """ constructor
        @param context: context object
               data :  ISynchroData object
               importer : IZexpImporter plugin """


        self.context = context
        self.data = data
        self.importer = importer

    def __call__(self):
        """ return import context for zexp """

        context = self.context
        import_path = None
        try:
            import_path = self.data.getImportPath()
        except:
            config.logger.exception('can get synchro path fo data')
            raise SynchroError("can't get synchro path")

        container = context.unrestrictedTraverse(import_path,
                                                 None)
        if container is None:
            config.logger.exception('can get synchro path %s' % import_path)
            raise SynchroError("Import path is not available")
        if self.data.getId() in container.objectIds():
            ## try to delete the current item in container
            to_delete = container[self.data.getId()]
            config.logger.info('delete %s in %s' % (self.data.getId(),
                                '/'.join(container.getPhysicalPath())))

            ## unlock item if it locked
            lockable = queryAdapter(to_delete, ILockable, default = None)
            if lockable and lockable.locked():
                 noLongerProvides(to_delete, INonStealableLock)
                 lockable.clear_locks()
            ## delete item
            container.manage_delObjects([self.data.getId(),])


        return container


class DeleteImportContext(object):

    implements(IImportContext)
    adapts(Interface, ISynchroData, IDeleteImporter)

    def __init__(self, context, data, importer):
        """ constructor
        @param context: context object
               data :  ISynchroData object
               importer : IZexpImporter plugin """

        self.context = context
        self.data = data
        self.importer = importer

    def __call__(self):
        """ return import context for zexp """
        return self.context.unrestrictedTraverse(self.data.getImportPath(),
                                                 None)


class FssImportContext(object):

    implements(IImportContext)
    adapts(Interface, ISynchroData, IFssImporter)

    def __init__(self, context, data, importer):
        """ constructor
        @param context: context object
               data :  ISynchroData object
               importer : IZexpImporter plugin """

        self.context = context
        self.data = data
        self.importer = importer

    def __call__(self):
        """ return import context for zexp """

        return self.context.restrictedTraverse(self.data.getImportPath(), None)




class DefaultImportContext(object):

    implements(IImportContext)
    adapts(Interface, ISynchroData, IPluginImporter)

    def __init__(self, context, data, importer):
        """ constructor
        @param context: context object
               data :  ISynchroData object
               importer : IZexpImporter plugin """

        self.context = context
        self.data = data
        self.importer = importer

    def __call__(self):
        """ return import context for zexp """

        return self.context.restrictedTraverse( '/'.join(self.data.path ))

