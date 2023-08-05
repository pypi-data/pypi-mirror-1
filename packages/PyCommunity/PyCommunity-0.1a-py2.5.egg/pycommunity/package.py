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
""" package doc builder
"""
import os
import logging

from Cheetah.Template import Template
try:
    from epydoc.cli import write_html
    from epydoc.docbuilder import build_doc_index
    epydoc = True
except ImportError:
    epydoc = False

try:
    from cheesecake.cheesecake_index import Cheesecake
    cheese = True
except ImportError:
    cheese = False

from generator import registerTask
from resttask import TaskView
from utils import extractHtmlContent
from utils import rest2Web

class PackageIndexView(object):
    """renders the package index"""
    def __init__(self, templatefile, folder, options):
        indexdoc, otherdocs = self._computeDocList(folder)

        self._template = Template(open(templatefile).read(),
                                  searchList=[{'docs': otherdocs,
                                               'main': indexdoc[1],
                                               'title': indexdoc[0],
                                               'options': options}])

    def _computeDocList(self, folder):
        """gathers a list of all docs

        and a reST render of README.txt if founded
        """
        docs = []
        indexdoc = None, None
        for element in os.listdir(folder):
            fullpath = os.path.join(folder, element)
            fullpath = os.path.realpath(fullpath)
            if os.path.isfile(fullpath):
                if element.lower() == 'index.html':
                    # we don't want it listed
                    pass
                elif element.lower() == 'readme.html':
                    # let's grab its content, to inject it in 
                    # the index
                    indexdoc = extractHtmlContent(fullpath)
                else:
                    title, body = extractHtmlContent(fullpath)
                    webpath = './%s' % element
                    docs.append((title, webpath))
        return indexdoc, docs

    def render(self):
        """renders the html"""
        return str(self._template)
    __call__ = render

class PackagesIndexView(object):
    """renders the global index"""
    def __init__(self, templatefile, folder, options):
        packages = self._computePackageList(folder)
        title, content = rest2Web(options['packages'])
        self._template = Template(open(templatefile).read(),
                                  searchList=[{'packages': packages,
                                               'options': options,
                                               'title': title,
                                               'content': content}])

    def _computePackageList(self, folder):
        """gathers a list of all subfolders"""
        dirs = []
        for element in os.listdir(folder):
            fullpath = os.path.join(folder, element)
            if os.path.isdir(fullpath):
                webpath = './%s' % element
                dirs.append((element, webpath))
        return dirs

    def render(self):
        """renders the html"""
        return str(self._template)
    __call__ = render

class PackageTask(object):
    """creates the documentation for packages"""

    def _writeFile(self, name, content):
        """write a file"""
        f = open(name, 'w')
        logging.info('writing %s' % name)
        try:
            f.write(content)
        finally:
            f.close()

    def _getName(self):
        return 'package'
    
    def _makeDirectory(self, path):
        """check that the given directory exists"""
        if os.path.exists(path):
            return
        os.makedirs(path)

    def _getFiles(self, folder, extension):
        """lists all files, given an extension"""
        ffiles = []
        for root, dirs, files in os.walk(folder):
            for file_ in files:
                if not file_.endswith('.%s' % extension):
                    continue
                file_ = os.path.join(root, file_)
                ffiles.append(os.path.realpath(file_))
        return ffiles

    def _listSources(self, folder):
        """lists all python files, given a folder, recursive"""
        return self._getFiles(folder, 'py')

    def _getRestFiles(self, folder):
        """lists all rest file, given a folder recursive"""
        return self._getFiles(folder, 'txt')

    def _run(self, configuration):
        """generates packages"""
        targets = configuration.targets.values()
        packages = configuration.packages.values()
        self._rest_template = configuration.templates['packagedoc']
        self._stats_template = configuration.templates['packagestats']
        self._index_template = configuration.templates['packageindex']
        self._global_index_template = configuration.templates['packagesindex']
        self._glossary_file = configuration.glossary
        self._options = configuration.options
        self._tutorials = configuration.tutorials
        self._recipes = configuration.recipes

        for target in targets:
            root = os.path.join(target, 'packages')
            root = os.path.realpath(root)

            # making the top directory if needed
            self._makeDirectory(root)

            for package in packages:

                basename = os.path.split(package)[-1]
                package_root = os.path.join(root, basename)

                # making the directory if needed
                self._makeDirectory(package_root)

                # collecting the reST files and generating them
                restfiles = self._getRestFiles(package)
                self._makeRestFiles(restfiles, package_root)
 
                # generating APIs with epydoc
                self._makeAPIs(package, package_root)

                # generating stats page
                self._makeStats(package, package_root)
                
                # making the package index
                self._makeIndex(package_root)

            # making the packages index
            self._makeGlobalIndex(root)

    def _getHTMLName(self, filename):
        """compute html file"""
        base = os.path.split(filename)[-1].split('.')[0]
        return '%s.html' % base

    def _makeRestFiles(self, files, folder):
        """generates rest files into the given folder"""
        template = self._rest_template
        glossary = self._glossary_file
        tutorials = self._tutorials
        recipes = self._recipes

        for file_ in files:
            view = TaskView(template, file_, glossary, tutorials, recipes)
            filename = os.path.join(folder, self._getHTMLName(file_))
            self._writeFile(filename, view()[1])

    def _makeAPIs(self, package, folder):
        """generates epydoc docs"""
        if not epydoc:
            return
        class EpyDocOptions(object):
            def __init__(self, target):
                self.target = target
                self.verbose = False

        target = os.path.join(folder, 'epydoc')
        options = EpyDocOptions(target)
        names = self._listSources(package)
        try:
            docindex = build_doc_index(names, True, True,
                                       add_submodules=True)
        except (AttributeError, ValueError):
            # a zope package ?
            return 
        if docindex is None:
            # nothing to build
            return
        write_html(docindex, options)

    def _makeStats(self, package, folder):
        """generates stat page

        Using:
            - cheesecake
            - trace2html
        """
        return
        if cheese:
            # cheesecacke wants an egg or a tarball..
            indexer = Cheesecake(path=path)
            indexer.compute_cheesecake_index()
            indexer.cleanup()

    def _makeIndex(self, folder):
        """generates package index page

        wich contains a list of documents and 
        display README.txt's content in the main view 
        """
        template = self._index_template
        view = PackageIndexView(template, folder, self._options)
        filename = os.path.join(folder, 'index.html')
        self._writeFile(filename, view())

    def _makeGlobalIndex(self, folder):
        """generates global package index page"""
        template = self._global_index_template
        view = PackagesIndexView(template, folder, self._options)
        filename = os.path.join(folder, 'index.html')
        self._writeFile(filename, view())

registerTask(PackageTask)

