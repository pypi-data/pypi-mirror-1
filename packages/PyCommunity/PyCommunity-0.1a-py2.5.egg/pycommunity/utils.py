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
""" helpers
"""
from docutils.core import publish_string
from docutils.utils import SystemMessage
import re

# XXX this dependency suck, see how to remove it
from glossary import GlossaryReader

re_options = re.MULTILINE | re.IGNORECASE | re.DOTALL

re_body = re.compile(r'<body>(.*?)</body>', re_options)
re_title = re.compile(r'<h1 class="title">(.*?)</h1>', re_options)
re_backlinks = re.compile(r'<div class="backlink">(.*?)</div>', re_options)
re_head_title = re.compile(r'<title>(.*?)</title>', re_options)
re_glossary = (re.compile(r'{{glossary:([a-zA-Z0-9_\-]*?)}}', re_options),
               r"<acronym title='$2'>$1</a>")

doc_replacer = r"""
<a title='$1' alt='$1' href='$2'>$3</a>
<img src="../media/expand.png" onclick="toggleElement('expandable-$1')"/>
<div id="expandable-$1" class="expandable" style="display:none">
$4
<div>
"""
re_docs = (re.compile((r'{{(?:(?:recipe)|(?:tutorial)):'
                        '([a-zA-Z0-9_\-]*?)(?:\:(.*?))?}}'),
           re_options), doc_replacer)

def _extractRe(expr, content):
    """extracts a subcontent, given a compiled expression"""
    content = expr.findall(content)
    if content != []:
        return content[0].strip()
    return ''
    
def rest2Web(rest_file):
    """returns an html content"""
    source = open(rest_file).read()
    try:
        html = publish_string(source=source, writer_name='html')
    except SystemMessage, e:
        return 'Error', str(e)

    body = _extractRe(re_body, html)
    title = _extractRe(re_title, body)
    return title, body

def extractHtmlContent(html_file):
    """extract the title and the body"""
    html = open(html_file).read()
    body = _extractRe(re_body, html)
    title = _extractRe(re_title, body)
    return title, removeBackLinks(body)

def removeBackLinks(content):
    """removes backlinks"""
    return re_backlinks.sub('', content)

def extractHeadTitle(html_file):
    """gets the title"""
    html = open(html_file).read()
    return _extractRe(re_head_title, html)
  

def findDefinition(word, glossary):
    try:
        return glossary.getDefinition(word)
    except KeyError:
        return None

def _grabContent(type, name, tutorial_folders, recipe_folders):
    """gets a recipe or a turotial content"""
    return """<b>Soon</b>"""

def linkChecker(content, glossaryfile, tutorial_folders, recipe_folders):
    """changes links on the fly"""
    glossary = GlossaryReader(glossaryfile)

    def glossary_replacer(match):
        word = match.groups()[0]
        definition = findDefinition(word, glossary)
        if definition is None:
            return match.group()
        url = re_glossary[1]
        url = url.replace('$1', word)
        return url.replace('$2', definition)

    def docs_replacer(match):
        name = match.groups()[0]
        text = match.groups()[1]
        
        if 'recipe' in match.group():
            link = '../recipes/%s.html' % name
            content = _grabContent('recipes', name, tutorial_folders,
                                   recipe_folders)
        else:
            link = '../tutorials/%s.html' % name
            content = _grabContent('tutorials', name, tutorial_folders,
                                   recipe_folders)

        url = re_docs[1]
        url = url.replace('$1', name)
        if text is not None:
            url = url.replace('$3', text)
        else:
            url = url.replace('$3', name)

        url = url.replace('$2', link)
        
        return url.replace('$4', content)

    content = re_glossary[0].sub(glossary_replacer, content)
    content = re_docs[0].sub(docs_replacer, content)
    return content

