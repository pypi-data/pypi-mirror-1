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
fss plugin
"""
## for interface

from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.BaseUnit import BaseUnit
from Products.Archetypes.config import TOOL_NAME
from zLOG import LOG, DEBUG, INFO

from collective.synchro.data import FssPluginData
from collective.synchro.interfaces import IFssExporter
from collective.synchro.interfaces import IFssImporter
from collective.synchro import config

# specific import

if config.HAS_FSS_27:
    from iw.fss.FileSystemStorage import FileSystemStorage
elif config.HAS_FSS_26:
    from Products.FileSystemStorage.FileSystemStorage import FileSystemStorage



class FssExporter:
    """
    fss plugin dispatcher
    """

    implements(IFssExporter)

    def __init__(self, context):
        self.context = context


    def _getListAttributeStorage(self):
        """
        return a dictionnary listing of all fss fields
        portal_type => (field1, field2)
        """
        if not config.HAS_FSS:
            return ()
        attool =  getToolByName(self.context, "archetype_tool")
        rtypes = attool.listRegisteredTypes()

        fss_fields={}
        ## list types
        for rtype in rtypes:
            ptype = rtype['portal_type']
            fieldnames = []
            schema = rtype['schema']

            for field in schema.fields():
                fieldname = field.getName()
                storage = field.storage
                ## test if storage is an FileSystemStorage
                if isinstance(storage, FileSystemStorage):
                    fieldnames.append(fieldname)
            # if one or more are fss we keep it in fss_fields
            if fieldnames:
                fss_fields[ptype] = fieldnames
        return fss_fields


    def exportData(self):
        """
        export an IPlugginData
        """
        context=self.context
        # Content class use to import fss data
        dataexport=FssPluginData()

        fss_fields=self._getListAttributeStorage()
        if fss_fields:
            ctool = getToolByName(context,'portal_catalog')
            query={'portal_type':fss_fields.keys(),
                   'path':'/'.join(self.context.getPhysicalPath())
                   }
            ## query all fss content type
            brains = ctool(**query)
            objs=[]
            if len(brains):
                objs = [ br.getObject() for br in brains ]
            ## and now we construct the file exporter
            storage = FileSystemStorage()

            for obj in objs:
                fnames = fss_fields[obj.portal_type]
                for fname in fnames :
                    f = obj.getField(fname)
                    value = storage.get(fname,obj)
                    ## construct data unit to be set

                    if hasattr(value,'getData'):
                        value=value.getData()



                    #data = BaseUnit(
                    #    name=fname,
                    #    file=value,
                    #    instance=obj,
                    #    filename= f.getFilename(obj) ,
                    #    mimetype=f.getContentType(obj)
                    #    )
                    data = {
                            'file': value,
                            'filename':  f.getFilename(obj),
                            'mimetype' : f.getContentType(obj)
                            }
                    ## compute object relative url
                    portal_url=getToolByName(context,'portal_url')
                    context_path=portal_url.getRelativeContentPath(context)
                    obj_path= portal_url.getRelativeContentPath(obj)

                    relative_url= '/'.join(obj_path[len(context_path)-1:])
                    ## add data to be exported in dataexport
                    dataexport.getData().append([relative_url,fname,data])
        return dataexport


class FssImporter:
    """
    fss plugin importer
    """
    implements(IFssImporter)


    def __init__(self, data):
        self.data = data

    def importData(self,context):
        """
        import an IPluginData
        """

        data= self.data

        #base_url=context.absolute_url(relative=True)

        for (rurl,fname,infos) in data.getData():
            curl=rurl

            object=context.unrestrictedTraverse(curl, None)
            if object:
                base_unit = BaseUnit(
                                name = fname,
                                file = infos['file'],
                                instance = object,
                                filename= infos['filename'] ,
                                mimetype= infos['mimetype'],
                                )

                object.getField(fname).set(object,base_unit)






