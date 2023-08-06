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
zexp pluggin adapter
"""
# python

from random import random
import os

from collective.synchro.interfaces import IPluginExporter
from collective.synchro.interfaces import IZexpExporter

from collective.synchro.interfaces import IZexpImporter
from collective.synchro.data import ZexpPluginData

from zope.interface import implements

from App.config import getConfiguration


class ZexpExporter:
    """
    zexp plugin exporter
    """

    implements(IZexpExporter)

    def __init__(self, context):
        self.context = context



    def exportData(self):
        """
        export an IPlugginData
        """
        context = self.context
        zexpFile = context.getParentNode().\
            manage_exportObject(id=context.getId(),
                                download=True)
        return ZexpPluginData(zexpFile)



class ZexpImporter:

    implements(IZexpImporter)


    def __init__(self,data):
        self.data=data

    def importData(self,context):
        """
        import an IPluginData
        """

        ## to avoid conflicts betwen to dispatch
        filename="receivedZexp_%i.zexp" % (int(random() * 1000000),)
        cfg = getConfiguration()

        filepath = os.path.join(cfg.instancehome, 'import', filename)
        zfile = file(filepath, "wb")
        zfile.write(self.data.getData())
        zfile.close()

        context.manage_importObject(filename)
        os.remove(filepath)

        ## reindex object




