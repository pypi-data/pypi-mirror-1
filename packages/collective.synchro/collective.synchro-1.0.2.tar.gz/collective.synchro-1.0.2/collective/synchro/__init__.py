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



def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    import permissions
    import tools
    import config

    from Products.CMFCore.utils import ToolInit

    ToolInit( 'Synchronisation Tools'
                , tools=[tools.SynchronisationTool,]

                , icon='browser/images/portal_synchro.png'
            ).initialize( context )
