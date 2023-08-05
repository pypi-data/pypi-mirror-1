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
""" Index render
"""
import os
import logging
from shutil import copyfile

from Cheetah.Template import Template

from generator import BaseTask
from generator import registerTask
from utils import rest2Web

class IndexView(object):
    """renders a view using a cheetah template"""
    def __init__(self, templatefile, options):
        title, content = rest2Web(options['index'])
        self._template = Template(open(templatefile).read(),
                                  searchList=[{'options': options,
                                               'title': title,
                                               'content': content}])
        
    def render(self):
        """renders the html"""
        return str(self._template)
    __call__ = render

class IndexTask(BaseTask):
    """creates the index file"""

    def _getName(self):
        """returns the task name"""
        return 'index'

    def _copyStaticFile(self, path, target_folder):
        """copies static file into the target folder"""
        filename = os.path.split(path)[-1]
        target_file = os.path.join(target_folder, filename)
        logging.info('copying file to %s' % target_file)
        copyfile(path, target_file)

    def _run(self, configuration):
        """reads the glossary file, and generate
        the html file"""
        static_files = [configuration.templates[name] for name
                        in ('css', 'js')]
        media_folder = configuration.media
        targets = configuration.targets.values()
        view = IndexView(configuration.templates['index'],
                         configuration.options)
        result = view()
        for target in targets:
            path = os.path.join(target, 'index.html')
            path = os.path.realpath(path)
            self._writeFile(path, result)

            for file_ in static_files:
                self._copyStaticFile(file_, target)

            # copy the media folder
            logging.info('copying media')
            for file_ in os.listdir(media_folder):
                fullpath = os.path.join(media_folder, file_)
                if not os.path.isfile(fullpath):
                    continue
                target_folder = os.path.join(target, 'media')
                targetpath = os.path.join(target_folder, file_)
                if not os.path.exists(target_folder):
                    os.mkdir(target_folder)
                copyfile(fullpath, targetpath)
         
registerTask(IndexTask)

