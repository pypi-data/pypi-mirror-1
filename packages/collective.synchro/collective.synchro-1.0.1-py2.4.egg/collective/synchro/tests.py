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

import os
import unittest
import doctest
from StringIO import StringIO
from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

# To install Dummy content type
from Products.Archetypes.Extensions.utils import installTypes
from Products.Archetypes.tests.utils import mkDummyInContext
from transaction import commit

# Archetypes imports
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *

from collective.synchro import config


if config.HAS_FSS_27:
    from iw.fss.FileSystemStorage import FileSystemStorage \
        as Storage
    ztc.installProduct('iw.fss')
elif config.HAS_FSS_26:
    from Products.FileSystemStorage.FileSystemStorage import FileSystemStorage \
        as Storage
    ztc.installProduct('FileSystemStorage')
else:
    from Products.Archetypes.Storage import AttributeStorage as Storage


if config.HAS_PLONE25:
#    ztc.installProduct('CollectiveSynchroEvents')
    pass


## base test s
ptc.setupPloneSite()

flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE)

current_dir = os.path.dirname(__file__)

import collective.synchro


## base test schema, contains an file
schema = BaseFolderSchema.copy() + Schema((
        FileField(
            'file',
            storage=Storage()
            ),))

class DummyContent(BaseFolder):
    """ a dummy content """
    portal_type = meta_type = archetypes_name = 'Dummy'


    __implements__ = BaseFolder.__implements__



class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True

            zcml.load_config('configure.zcml',
                             collective.synchro)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

    def pdb(self, *args, **kw):

        pass
        return

    def create_fss_content(self, id):
        self.portal.invokeFactory('Folder','folderfss')
        mkDummyInContext(DummyContent,
                         oid=id,
                         context=self.portal['folderfss'],
                         schema = schema)
        doc = self.portal['folderfss'][id]
        doc.update(**{'file':StringIO('text')})

        mkDummyInContext(DummyContent,
                         oid=id,
                         context=doc,
                         schema = schema)
        doc = doc[id]
        doc.update(**{'file':StringIO('text')})


        commit()

    def install_portal_synchronisation(self):

        if config.HAS_PLONE3:
            self.portal.portal_quickinstaller.installProduct('collective.synchro')
        elif config.HAS_PLONE25:
            profile = 'profile-collective.synchro:collective.synchro'
            self.portal.portal_setup.setImportContext(profile)
            self.portal.portal_setup.runAllImportSteps()
        return 'portal_synchronisation' in self.portal.objectIds()

    def uninstall_portal_synchronisation(self):
        if config.HAS_PLONE3:
            self.portal.portal_quickinstaller.uninstallProducts(['collective.synchro',])
        elif config.HAS_PLONE25:
            self.portal.manage_delObjects('portal_synchronisation')
        return 'portal_synchronisation' not in self.portal.objectIds()

    def install_fss(self):
        pq = self.portal.portal_quickinstaller
        if config.HAS_FSS_27:
            pq.installProduct('iw.fss')
            return 'iw.fss' in [x['id'] for x in pq.listInstalledProducts()]
        elif config.HAS_FSS_26:
            pq.installProduct('FileSystemStorage')
            return  'FileSystemStorage' in [x['id'] for x in pq.listInstalledProducts()]
        else:
            return False

    def uninstall_fss(self):
        pq = self.portal.portal_quickinstaller
        if config.HAS_FSS_27:
            pq.uninstallProducts(['iw.fss',])
            return 'iw.fss' not in [x['id'] for x in pq.listInstalledProducts()]
        elif config.HAS_FSS_26:
            pq.uninstallProducts(['FileSystemStorage',])
            return  'FileSystemStorage' not in [x['id'] for x in pq.listInstalledProducts()]
        else:
            return False


def test_suite():
    docs = []
    suites = []

    for dir_ in ('doctests',):
        doctest_dir = os.path.join(current_dir, dir_)
        docs.extend([os.path.join(dir_, doc) for doc in
                     os.listdir(os.path.join(current_dir, dir_)) if doc.endswith('.txt')])
    for test in docs:
        suites.append(ztc.FunctionalDocFileSuite(
            test, package='collective.synchro',
            test_class=TestCase, optionflags=flags),)
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
