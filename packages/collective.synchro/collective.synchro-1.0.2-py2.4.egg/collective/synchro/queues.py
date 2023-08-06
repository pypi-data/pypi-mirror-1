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
import random
from time import time

from zope.interface import implements

from interfaces.queues import IQueue
from interfaces import ISynchroData
from cPickle import load
from cPickle import dump
from cPickle import PickleError
from scripts.utils import create_queue_structure
from scripts.utils import LEVEL_ONE
from scripts.utils import LEVEL_TWO
from scripts.utils import good_name
from scripts.utils import islock



import config

class Queue(object):

    implements(IQueue)

    def __init__(self, path):
        """ constructor of a queue """

        self.path = path
        create_queue_structure(self)

    def put(self, data):
        """ export data in a queue
            @param : data an ISynchroData
            @return : filename in system or None if not succedd
        """

        if ISynchroData.providedBy(data):
            randint = random.randint(0, 1000000)
            uid = data.getUid()
            t = time()
            file_name_lock = 'data_%s_%f_%d.zs.lock' % (uid, t, randint)
            file_name = 'data_%s_%f_%d.zs' % (uid, t, randint)
            file_path_lock = os.path.join(self.export_to_process_path,
                                          file_name_lock)
            file_path = os.path.join(self.export_to_process_path,
                                          file_name)

            try:
                fd = open(file_path_lock,
                            'wb')
                try:
                    dump(data, fd)
                except PickleError ,e:
                    fd.close()
                    os.unlink(file_path_lock)
                    config.logger.exception("can't pickle data")
                    return
                fd.close()
            except IOError, e:
                config.logger.exception("can't pickle data")
                return
            fd.close()
            ## Unlock file
            os.rename(file_path_lock, file_path)
            config.logger.info("put %s to be imported" % file_path)
            return file_path


    def listQueue(self, type = 'EXPORT', queue = 'TO_PROCESS'):
        """ list element in queue """

        files = os.listdir(getattr(self,
                                   '%s_%s_path' % (type.lower(),queue.lower())
                            ))
        files.sort(lambda x,y:cmp(float(good_name(x).groups()[1]),
                                  float(good_name(y).groups()[1]))
                                  )
        return files

    def importFile(self, context, file_name ):
        """ import data in context
            @param : context : the context of the import
                     file : file wich contains data
        """

        to_process_file_name = os.path.join(self.import_to_process_path, file_name)
        processing_file_name = os.path.join(self.import_processing_path, file_name)
        done_file_name = os.path.join(self.import_done_path, file_name)
        error_file_name = os.path.join(self.import_error_path, file_name)
        ## copy file_name in process file
        os.rename(to_process_file_name, processing_file_name)
        fd = None
        ## unpickle data
        try:
            fd = open(processing_file_name,'r')
            data = load(fd)
        except PickleError,e:
            fd.close()
            config.logger.exception("can't unpickle data %s" % file_name)
            os.rename(processing_file_name, error_file_name)
            return
        except Exception,e:
            config.logger.exception("error in reading file %s" % file_name)
            os.rename(processing_file_name, error_file_name)
            return
        if fd is not None:
            fd.close()
        ## now reimport to context
        try:
            data(context)
        except Exception,e:
            config.logger.exception("error in import file %s" % file_name)
            os.rename(processing_file_name, error_file_name)
            return
        config.logger.info("import %s is ok" % file_name)
        os.rename(processing_file_name, done_file_name)







