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
""" Configuration reader
"""
import os
from ConfigParser import ConfigParser

class Configuration(object):
    """loads a config file"""

    def __init__(self, filename):
        self._filename = filename
        self._config = ConfigParser()
        self._config.read([filename])

    def _getItems(self, name):
        """return a mapping for a given section"""
        result = {}
        for name, value in self._config.items(name):
            result[name] = value
        return result

    def _getRecipes(self):
        """returns recipe list"""
        return self._getItems('recipes')
    recipes = property(_getRecipes)

    def _getPackages(self):
        """returns packages list"""
        return self._getItems('packages')
    packages = property(_getPackages)

    def _getTutorials(self):
        """returns tutorial list"""
        return self._getItems('tutorials')
    tutorials = property(_getTutorials)

    def _getGlossary(self):
        """returns glossary"""
        return self._getItems('options')['glossary']
    glossary = property(_getGlossary)

    def _getMedia(self):
        """returns media"""
        return self._getItems('options')['media']
    media = property(_getMedia)

    def _getTargets(self):
        """returns targets"""
        return self._getItems('targets')
    targets = property(_getTargets)

    def _getTemplates(self):
        """returns templates"""
        return self._getItems('templates')
    templates = property(_getTemplates)

    def _getOptions(self):
        """returns options"""
        return self._getItems('options')
    options = property(_getOptions)

