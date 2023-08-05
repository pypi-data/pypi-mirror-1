#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2006 Tarek Ziadé <tarek@ziade.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# $Id: $
""" Generator
"""
import logging

class BaseTask(object):
    """base class for task"""
    def _getName(self):
        raise NotImplementedError

    def _run(self, configuration):
        raise NotImplementedError

    def _writeFile(self, path, content):
        """helper to write a file"""
        f = open(path, 'w')
        logging.info('writing %s' % path)
        try:
            f.write(content)
        finally:
            f.close()

tasks = None

def registerTask(task):
    """registers a task"""
    global tasks
    if tasks is None:
        tasks = {}
    instance = task()
    tasks[instance._getName()] = instance

def run(steps, configuration):
    """runs a sequence"""
    for step in steps:
        tasks[step]._run(configuration)

