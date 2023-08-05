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
""" Glossary reader and render
"""
import os
import logging

from Cheetah.Template import Template
from generator import BaseTask
from generator import registerTask

class GlossaryReader(list):
    """reads glossary entries"""
    def __init__(self, filename):
        def _clean(element):
            element = element.lower()
            return element.strip()
        self.filename = filename
        words = []
        for line in open(filename):
            line = line.strip()
            if line.startswith('#'):
                continue
            elements = line.split(':')
            if len(elements) != 2:
                continue
            word = _clean(elements[0])
            if word in words:
                continue
            self.append((word, _clean(elements[1])))
            words.append(word)

    def getDefinition(self, word):
        """returns a definition"""
        word = word.lower()
        for word_, definition in self:
            if word_ == word:
                return definition
        raise KeyError('%s not found' % word)

class GlossaryView(object):
    """renders a view using a cheetah template"""
    def __init__(self, templatefile, glossary):
         self._glossary = glossary
         self._template = Template(open(templatefile).read(),
                                   searchList=[{'glossary': glossary}])
        
    def render(self):
        """renders the html"""
        return str(self._template)
    __call__ = render

class GlossaryTask(BaseTask):
    """creates the glossary file"""

    def _getName(self):
        """returns the task name"""
        return 'glossary'

    def _run(self, configuration):
        """reads the glossary file, and generate
        the html file"""
        targets = configuration.targets.values()
        glossary = GlossaryReader(configuration.glossary)
        # XXX see if we want to externalize this path
        view = GlossaryView(configuration.templates['glossary'], glossary)
        result = view()
        for target in targets:
            path = os.path.join(target, 'glossary.html')
            path = os.path.realpath(path)
            logging.info('writing %s' % path)
            glossary_file = open(path, 'w')
            try:
                glossary_file.write(result)
            finally:
                glossary_file.close()

registerTask(GlossaryTask)

