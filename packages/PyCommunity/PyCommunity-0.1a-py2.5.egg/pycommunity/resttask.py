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
""" reSTructuredText base task
"""
import os
import logging

from Cheetah.Template import Template
from utils import rest2Web
from utils import extractHeadTitle
from utils import linkChecker
from generator import BaseTask

class TaskView(object):
    """generates a base view"""
    def __init__(self, templatefile, restfile, glossaryfile, tutorial_folders,
                 recipe_folders):
        title, content = rest2Web(restfile)
        content = linkChecker(content, glossaryfile, tutorial_folders,
                              recipe_folders)
        self.title = title
        self._template = Template(open(templatefile).read(),
                                  searchList=[{'content': content,
                                               'title': title}])

    def render(self):
        """renders the html"""
        return self.title, str(self._template)
    __call__ = render

class TaskListView(TaskView):
    """generates a base view for lists"""
    def __init__(self, templatefile, filelist, title):
        self.title = title
        self._template = Template(open(templatefile).read(),
                                  searchList=[{'files': filelist,
                                                'title': title}])

class RestTask(BaseTask):
    """creates the html content"""
    _templatefile = None
 
    def _getRestFiles(self, folder):
        """lists all rest file, given a folder"""
        files = []
        for file_ in os.listdir(folder):
            if file_.endswith('.txt'):
                files.append(file_)
        return [os.path.realpath(os.path.join(folder, file_))
                for file_ in files]

    def _getFolders(self, configuration):
        """returns the folders"""
        raise NotImplementedError

    def _getTemplateFile(self, configuration):
        """returns the template"""
        raise NotImplementedError

    def _getTemplateListFile(self, configuration):
        """returns the template list"""
        raise NotImplementedError

    def _run(self, configuration):
        """generates recipes"""
        targets = configuration.targets.values()
        folders = self._getFolders(configuration)

        for folder in folders:
            # not recursive
            restfiles = self._getRestFiles(folder)
                                
            for target in targets:
                
                # making the subfolder
                subfolder = os.path.join(target, '%ss' % self._getName())
                if not os.path.exists(subfolder):
                    os.mkdir(subfolder)

                # creating files
                titles = []
                for restfile in restfiles:
                    # generating the view
                    view = TaskView(self._getTemplateFile(configuration),
                                    restfile, configuration.glossary,
                                    configuration.tutorials,
                                    configuration.recipes)
                    title, result = view()
                    titles.append(title)
                    # calculating the file path  
                    file_name = os.path.split(restfile)[-1].split('.')[0]
                    path = os.path.join(subfolder, '%s.html' % file_name)
                    path = os.path.realpath(path)
                    logging.info('writing %s' % path)
                    html_file = open(path, 'w')
                    try:
                        html_file.write(result)
                    finally:
                        html_file.close()

                # making the root file, with the real
                # content of the subfolder, that can
                # contains more than what the present loop does
                def getFileInfos(folder, file_):
                    path = os.path.join(folder, file_)
                    title = extractHeadTitle(path)
                    url = '%ss/%s' % (self._getName(), file_)
                    return title, url

                restfiles = [getFileInfos(subfolder, file_)
                             for file_ in os.listdir(subfolder)
                             if file_.endswith('.html')]
                
                rootfile = os.path.join(target, '%ss.html' % self._getName())
                view = TaskListView(self._getTemplateListFile(configuration),
                                    restfiles, self._getName())
                title, result = view()
                rootfile = os.path.realpath(rootfile)
                logging.info('writing %s' % rootfile)
                html_file = open(rootfile, 'w')
                try:
                    html_file.write(result)
                finally:
                    html_file.close()

