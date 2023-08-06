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
import re
import sys
from subprocess import Popen
from tempfile import gettempdir

good_name = re.compile(r'data_([^_]*)_([^_]*)_([^\.]*).zs').match
islock = re.compile(r'.*\.lock').match
LEVEL_ONE = ['EXPORT', 'IMPORT']
LEVEL_TWO = ['TO_PROCESS', 'PROCESSING', 'DONE', 'ERROR']

def create_queue_structure(self):
    """ create an structure of queue """
    path = self.path
    ## make sure that path exists
    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except:
            config.logger.exception('can not create path')
            raise
    for t in LEVEL_ONE:
        if not os.path.exists(os.path.join(path,t)):
            try:
                os.mkdir(os.path.join(path,t))
            except:
                __traceback_info__ = (self, os.path.join(path,t))
                config.logger.exception('can not create path %s' % \
                                        (os.path.join(path,t)))
                raise

        for p in LEVEL_TWO:
            if not os.path.exists(os.path.join(path,t,p)):
                try:
                    os.mkdir(os.path.join(path,t,p))
                except:
                    __traceback_info__ = (self, os.path.join(path,t,p))
                    config.logger.exception('can not create path %s' % \
                                             (os.path.join(path,t,p)))
                    raise

            setattr(self, "%s_%s_path" % (t.lower(),p.lower()),
                    os.path.join(path,t,p))

def is_valid(path):
    """ verify that queue is good """

    for t in LEVEL_ONE:
        for p in LEVEL_TWO:
            if not os.path.exists(os.path.join(path,t,p)):
                return False
    return True

def lock(file_name_lock, logger):
    """ verify that process is lock """

    mypid  = os.getpid()
    if os.path.exists(file_name_lock):
        pid = open(file_name_lock, 'r').read().strip()
        if pid == mypid:
            ## same pid
            return False
            ## verify that process is working

        stdout = open(os.path.join(gettempdir(),'out'),'w')
        stderr = open(os.path.join(gettempdir(),'err'),'w')
        p = Popen('ps -p %s | wc -l' % (pid,),
                  stdout= stdout,
                  stderr= stderr,
                  shell = True)
        sts = os.waitpid(p.pid, 0)
        stdout.close()
        stderr.close()
        r = open(os.path.join(gettempdir(),'out'),'r')
        n = None
        try:
            n = int(r.read().strip())
        except ValueError,e:
            logger.exception("wc -l must be return an int")
            raise
        if n is not None:
            if n > 1:
                ## the process is running
                raise SystemExit('This process is lock %s' % (file_name_lock))
            else:
                logger.info("the lock file is present but not process")
    fd = open(file_name_lock, 'w')
    fd.write(str(mypid))
    fd.close()

def unlock(file_name_lock):
    """ unlock file """

    os.unlink(file_name_lock)

