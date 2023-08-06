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

__doc__ = """ events system to synchronize content """

from zope.interface import implements
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryUtility
from OFS.interfaces import ISimpleItem

from interfaces import ISynchroData
from interfaces.tool import ISynchronisationTool
from interfaces.events import ISynchroModifiedEvent
from interfaces.events import ISynchroDeletedEvent


from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import getExprContext
from Products.CMFCore.utils import getToolByName

import config

def test(object, event):
    print "je passe dans collective.synchro"



def synchro(object, event):
    synchro_tool = getToolByName(object, 'portal_synchronisation',
                                 None)

    if synchro_tool is not None and \
        isinstance(synchro_tool._expression,Expression):
        ##call _getExprContext and no getExprContext from Expression because
        ##
        exp_context = synchro_tool._getExprContext(object)
        synchro = False
        try:
            synchro = synchro_tool._expression(exp_context)
        except:
            config.logger.exception('error expression for %s ' % \
                                    '/'.join(object.getPhysicalPath()))
        if synchro:

            ## expression is validatedc
            config.logger.info("synchro content %s" % \
                          '/'.join(object.getPhysicalPath() ))
            try:
                data = getMultiAdapter((object,event), ISynchroData)
                synchro_tool.exportContent(data)
            except:
                __traceback_info__ = (object, event)
                config.logger.exception('error in synchro content for %s ' % \
                                    '/'.join(object.getPhysicalPath()))

class SynchroModifiedEvent(object):
    implements(ISynchroModifiedEvent)

    def __init__(self, object = None):
        self.object = object

class SynchroDeletedEvent(object):
    implements(ISynchroDeletedEvent)

    def __init__(self, object = None):
        self.object = object
