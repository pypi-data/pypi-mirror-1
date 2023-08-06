#!/usr/bin/env python
# ex:ts=8:sw=4:sts=4:et
# -*- tab-width: 8; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Copyright (C) 2008 Marco Pantaleoni. All rights reserved

"""
sf-import-twiki

Tool for importing (converting) twiki wikis into softwarefabrica wikis).

To generate documentation for this program, use epydoc.
To perform doctests, invoke with '-t'.
To get help, invoke with '-h'.

@author: Marco Pantaleoni
@contact: Marco Pantaleoni <panta@elasticworld.org>
@contact: Marco Pantaleoni <marco.pantaleoni@gmail.com>
@copyright: Copyright (C) 2008 Marco Pantaleoni. All rights reserved.

@see: ...


@todo: command-line option parsing
@todo: write doctests
@todo: handle qualified (nested) target wiki names
"""

import sys, os, getopt, glob
import re, string, StringIO
import datetime
import optparse

import signal as unixsignal
import logging

from sflib import udom
from sflib import visitor

PROGNAME    = "sf-import-twiki"
__version__ = "1.0.0"
__svnid__   = "$Id$"
__license__ = "GPL"
__author__  = "Marco Pantaleoni <panta@elasticworld.org>"


# # -- calculate project root ----------------------------------------------

# pjoin = lambda *p: reduce(os.path.join, p)

# DJANGO_PROJECT_NAME = 'testproj'

# this_mod = __import__(__name__)
# CUR_DIR  = os.path.abspath(os.path.dirname(this_mod.__file__))
# PROJECT_DIR   = os.path.dirname(CUR_DIR)
# TOP_LEVEL_DIR = os.path.dirname(PROJECT_DIR)
# PYTHON_LIBS   = pjoin(PROJECT_DIR, 'libs')
# DJANGO_SRC    = pjoin(PYTHON_LIBS, 'django_src')

# #DJANGO_SETTINGS_MODULE = DJANGO_PROJECT_NAME + '.settings'
# DJANGO_SETTINGS_MODULE = DJANGO_PROJECT_NAME + '.settings_real'
# os.environ['DJANGO_SETTINGS_MODULE'] = DJANGO_SETTINGS_MODULE

# sys.path.append(DJANGO_SRC)
# sys.path.append(PYTHON_LIBS)
# sys.path.append(CUR_DIR)
# sys.path.append(TOP_LEVEL_DIR)

def check_django_settings():
    if 'DJANGO_SETTINGS_MODULE' not in os.environ:
        sys.stderr.write("""Error: Settings cannot be imported, because environment variable DJANGO_SETTINGS_MODULE is undefined.

Please either pass the '--settings' option or define the
'DJANGO_SETTINGS_MODULE' environment variable, making it
point to your django wiki project settings file.
""")
        sys.exit(1)
        return False
    return True

# -- Django imports ------------------------------------------------------

from django.core.exceptions import ObjectDoesNotExist
#from softwarefabrica.django.wiki.models import *
from softwarefabrica.django.wiki import version

# -- Defaults ------------------------------------------------------------

DEFAULT_INPUT_DIR     = "/arc/twiki-data/data/Main"
DEFAULT_TARGET_WIKI   = "Main"

LOGGING_CONF_FILE     = os.path.join(os.path.dirname(__file__), 'twiki-import-log.conf')

SKIP_TWIKI_FILES = ("NobodyGroup.txt", "PatternSkinUserViewTemplate.txt",
                    "PublishForm.txt",
                    "TWikiAdminGroup.txt", "TWikiContributor.txt",
                    "TWikiGroups.txt", "TWikiGuestLeftBar.txt",
                    "TWikiPreferences.txt", "TWikiUsers.txt",
                    "TWikiContributor.txt", "TWikiGroupTemplate.txt",
                    "TWikiGuest.txt", "TWikiRegistrationAgent.txt",
                    "UnknownUser.txt",
                    "UserForm.txt",
                    "UserHomepageHeader.txt",
                    "UserListByDateJoined.txt",
                    "UserListByLocation.txt",
                    "UserListByPhotograph.txt",
                    "UserListHeader.txt",
                    "UserList.txt",
                    "UserViewTemplate.txt",
                    "WebAtom.txt",
                    "WebSearchAdvanced.txt",
                    "WebSearch.txt",
                    "WebTopicCreator.txt",
                    "WebChanges.txt", "WebIndex.txt", "WebLeftBar.txt",
                    "WebNotify.txt", "WebPreferences.txt", "WebRss.txt",
                    "WebStatistics.txt",
                    "WebTopicList.txt",)

# -- Constants -----------------------------------------------------------

VERBOSITY_QUIET   = 0
VERBOSITY_NORMAL  = 1
VERBOSITY_VERBOSE = 2
VERBOSITY_DEBUG   = 3

# -- Globals -------------------------------------------------------------

log = logging.getLogger('TWikiImport')
dbg = logging.getLogger('TWikiImport.Debug')

#============================================================================#
# Utility functions
#============================================================================#

#============================================================================#
# Application class
#============================================================================#

class DocumentEntity(udom.Entity):
    def __init__(self, *args, **kwargs):
        text = None
        if 'text' in kwargs:
            text = kwargs['text']
            del kwargs['text']
        super(DocumentEntity, self).__init__(*args, **kwargs)
        if text is not None:
            self.appendChild(self.createTextElement(text))

    def createTextElement(self, text):
        el = Text(text = text)
        return el

    def addText(self, text):
        el = Text(text = text)
        self.appendChild(el)
        return self

class Document(DocumentEntity):
    NAME = 'document'

class Text(DocumentEntity):
    NAME = 'text'

    def __init__(self, text, *args, **kwargs):
        super(Text, self).__init__(*args, **kwargs)
        self.text = text

    def __repr__(self):
        attr_r = ""
        for k, v in self.attrs:
            attr_r += " %s=%s" % (k, repr(v))
        tagName = self.getElementTagName()
        children_r = ""
        for child in self.children:
            children_r += repr(child)
        text_u = unicode(self.text)
        text_a = text_u.encode('ascii', 'replace')
        r = "<%s%s>%s%s</%s>" % (tagName, attr_r, text_a, children_r, tagName)
        return r

class Paragraph(DocumentEntity):
    NAME = 'paragraph'

class Emphasis(DocumentEntity):
    NAME = 'emphasis'

class Strong(DocumentEntity):
    NAME = 'strong'

class EmphasisStrong(DocumentEntity):
    NAME = 'emphasisstrong'

class Link(DocumentEntity):
    NAME = 'link'

    def __init__(self, url, *args, **kwargs):
        super(Link, self).__init__(*args, **kwargs)
        self.url = url

    def __repr__(self):
        attr_r = ""
        for k, v in self.attrs:
            attr_r += " %s=%s" % (k, repr(v))
        tagName = self.getElementTagName()
        children_r = ""
        for child in self.children:
            children_r += repr(child)
        r = "<%s%s>%s%s</%s>" % (tagName, attr_r, self.url, children_r, tagName)
        return r

class WikiLink(DocumentEntity):
    NAME = 'wikilink'

    def __init__(self, target, desc, *args, **kwargs):
        super(WikiLink, self).__init__(*args, **kwargs)
        self.target = self.wiki_escape_target(target)
        self.desc   = desc

    def wiki_escape_target(self, text):
        text = re.sub(r' ', "_", text, 0)
        text = re.sub(r'\|', "+", text, 0)
        return text

    def __repr__(self):
        attr_r = ""
        for k, v in self.attrs:
            attr_r += " %s=%s" % (k, repr(v))
        tagName = self.getElementTagName()
        children_r = ""
        for child in self.children:
            children_r += repr(child)
        r = "<%s%s>%s \"%s\" %s</%s>" % (tagName, attr_r, self.target, self.desc, children_r, tagName)
        return r

class AttachmentLink(DocumentEntity):
    NAME = 'attachmentlink'

    def __init__(self, target, desc, *args, **kwargs):
        super(AttachmentLink, self).__init__(*args, **kwargs)
        self.target = target
        self.desc   = desc

    def __repr__(self):
        attr_r = ""
        for k, v in self.attrs:
            attr_r += " %s=%s" % (k, repr(v))
        tagName = self.getElementTagName()
        children_r = ""
        for child in self.children:
            children_r += repr(child)
        r = "<%s%s>%s \"%s\" %s</%s>" % (tagName, attr_r, self.target, self.desc, children_r, tagName)
        return r

class CodeSpan(DocumentEntity):
    NAME = 'codespan'

class LineBreak(DocumentEntity):
    NAME = 'linebreak'

class HR(DocumentEntity):
    NAME = 'hr'

class Header(DocumentEntity):
    NAME = 'header'
    DEFAULT_ATTRIBUTES = {'level': 1}

    def __init__(self, *args, **kwargs):
        super(Header, self).__init__(*args, **kwargs)
        self.level = self.attrs['level']

class BlockQuote(DocumentEntity):
    NAME = 'blockquote'

class List(DocumentEntity):
    NAME = 'list'

    def __init__(self, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.level = self.attrs['level']

class ListItem(DocumentEntity):
    NAME = 'listitem'

class OrderedList(DocumentEntity):
    NAME = 'orderedlist'

    def __init__(self, *args, **kwargs):
        super(OrderedList, self).__init__(*args, **kwargs)
        self.level = self.attrs['level']

class ListItem(DocumentEntity):
    NAME = 'listitem'

class CodeBlock(DocumentEntity):
    NAME = 'codeblock'

operation_generate_markdown = visitor.Operation('generate_markdown')

class Document_operator_generate_markdown(visitor.Operator):
    def Perform(self, visited):
        r = ""
        for child in visited.children:
            r += child.Perform(operation_generate_markdown)
        return r

class Text_operator_generate_markdown(visitor.Operator):
    def markdown_escape_text(self, text):
        text = re.sub(r'\*', "\\*", text, 0)
        text = re.sub(r'\_', "\\_", text, 0)
        text = re.sub(r'\`', "\\`", text, 0)
        return text

    def Perform(self, visited):
        r = "%s" % self.markdown_escape_text(visited.text)
        for child in visited.children:
            r += child.Perform(operation_generate_markdown)
        return r

class Paragraph_operator_generate_markdown(visitor.Operator):
    def Perform(self, visited):
        r = ""
        for child in visited.children:
            r += child.Perform(operation_generate_markdown)
        r += "\n"
        return r

class Emphasis_operator_generate_markdown(visitor.Operator):
    def Perform(self, visited):
        r = "_"
        for child in visited.children:
            r += child.Perform(operation_generate_markdown)
        r += "_"
        return r

class Strong_operator_generate_markdown(visitor.Operator):
    def Perform(self, visited):
        r = "**"
        for child in visited.children:
            r += child.Perform(operation_generate_markdown)
        r += "**"
        return r

class EmphasisStrong_operator_generate_markdown(visitor.Operator):
    def Perform(self, visited):
        r = "_**"
        for child in visited.children:
            r += child.Perform(operation_generate_markdown)
        r += "**_"
        return r

class Link_operator_generate_markdown(visitor.Operator):
    def Perform(self, visited):
        c_t = ""
        for child in visited.children:
            c_t += child.Perform(operation_generate_markdown)
        r = "[%s](%s)" % (visited.url, visited.url)
        return r

class WikiLink_operator_generate_markdown(visitor.Operator):
    def Perform(self, visited):
        c_t = ""
        for child in visited.children:
            c_t += child.Perform(operation_generate_markdown)
        if visited.desc is not None:
            r = "[[%s|\"%s\"]]" % (visited.target, visited.desc)
        else:
            r = "[[%s]]" % (visited.target)
        return r

class AttachmentLink_operator_generate_markdown(visitor.Operator):
    def Perform(self, visited):
        c_t = ""
        for child in visited.children:
            c_t += child.Perform(operation_generate_markdown)
        if visited.desc is not None:
            r = "[[attachment:%s|\"%s\"]]" % (visited.target, visited.desc)
        else:
            r = "[[attachment:%s]]" % (visited.target)
        return r

class CodeSpan_operator_generate_markdown(visitor.Operator):
    def Perform(self, visited):
        r = "`"
        for child in visited.children:
            r += child.Perform(operation_generate_markdown)
        r += "`"
        return r

class LineBreak_operator_generate_markdown(visitor.Operator):
    def Perform(self, visited):
        r = ""
        for child in visited.children:
            r += child.Perform(operation_generate_markdown)
        r += "  \n"
        return r

class HR_operator_generate_markdown(visitor.Operator):
    def Perform(self, visited):
        r = ""
        for child in visited.children:
            r += child.Perform(operation_generate_markdown)
        r += "\n---\n"
        return r

class Header_operator_generate_markdown(visitor.Operator):
    def Perform(self, visited):
        r = ("#" * visited.level) + " "
        for child in visited.children:
            r += child.Perform(operation_generate_markdown)
        r += "\n\n"
        return r

class List_operator_generate_markdown(visitor.Operator):
    def Perform(self, visited):
        r = ""
        for child in visited.children:
            r += child.Perform(operation_generate_markdown)
        r += "\n"
        return r

class OrderedList_operator_generate_markdown(visitor.Operator):
    def Perform(self, visited):
        r = ""
        for child in visited.children:
            r += child.Perform(operation_generate_markdown)
        r += "\n"
        return r

class ListItem_operator_generate_markdown(visitor.Operator):
    def Perform(self, visited):
        parent = visited.parent
        if isinstance(parent, OrderedList):
            r = "1. " * parent.level
        else:
            r = "* " * parent.level
        for child in visited.children:
            r += child.Perform(operation_generate_markdown)
        r += "\n"
        return r

class CodeBlock_operator_generate_markdown(visitor.Operator):
    def Perform(self, visited):
        r = "\n"
        for child in visited.children:
            child_text = "%s" % child.Perform(operation_generate_markdown)
            c_fh = StringIO.StringIO(child_text)
            for line in c_fh.readlines():
                r += "    " + line
            c_fh.close()
        r += ""
        return r

class ConverterIO(object):
    def __init__(self, rootdom, text):
        self.rootdom  = rootdom or Document()
        self.src_text = text

        self._lines = None
        self._num_lines = 0
        self._next_line = 0

        self.read()
        self.parse()

    def read(self):
        fh = StringIO.StringIO(self.src_text)
        self._lines = []
        for line in fh.readlines():
            self._lines.append(line)
        fh.close()

        self._num_lines = len(self._lines)
        self._next_line = 0
        return self

    def remaining(self, consume=True):
        r = ""
        n = self._next_line
        while n < self._num_lines:
            r += self._lines[n]
            n += 1
        if consume:
            self._next_line = n
        return r

    def text_all(self):
        r = ""
        n = 0
        while n < self._num_lines:
            r += self._lines[n]
            n += 1
        return r

    def next_line(self):
        if self._next_line >= self._num_lines:
            return None
        line = self._lines[self._next_line]
        self._next_line += 1
        return line

    def peek_line(self):
        if self._next_line >= self._num_lines:
            return None
        line = self._lines[self._next_line]
        return line

    def unread_line(self):
        assert self._next_line > 0
        self._next_line -= 1
        return self

    def eof(self):
        return self._next_line >= self._num_lines

    def parse(self):
        "abstract"
        assert False

    def chomp(self, line):
        if line[-2:] == '\r\n':
            line = line[:-2]
        elif line[-1:] == '\n':
            line = line[:-1]
        return line

    def __str__(self):
        return repr(self.rootdom)

    def log(self, msg, verb=VERBOSITY_VERBOSE):
        app = Application.Instance()
        return app.log(msg, verb)

    def dbg(self, msg, verb=VERBOSITY_DEBUG):
        app = Application.Instance()
        return app.dbg(msg, verb)

    def warn(self, msg):
        app = Application.Instance()
        return app.warn(msg, verb)

    def err(self, msg):
        app = Application.Instance()
        return app.err(msg, verb)

class LineIO(ConverterIO):
    def __init__(self, text):
        super(LineIO, self).__init__(None, text)

    def parse(self):
        return False

def chomp(line):
    if line[-2:] == '\r\n':
        line = line[:-2]
    elif line[-1:] == '\n':
        line = line[:-1]
    return line

def get_li_level(c_io, line):
    m = re.match(r"(\t+)\*\s.*", line)
    if m:
        initial_tabs = m.group(1)
        n_tabs = len(initial_tabs)
        return n_tabs

    m = re.match(r"(\s+)\*\s.*", line)
    if m:
        initial_spaces = m.group(1)
        n_spaces = len(initial_spaces)
        if n_spaces % 3 == 0:
            return (n_spaces / 3)
        else:
            c_io.log("WRONG # of spaces: %s ('%s')" % (n_spaces, initial_spaces))
            return 0

    c_io.log("NOT A LIST '%s'" % line)
    return 0

def get_ol_li_level(c_io, line):
    m = re.match(r"(\t+)[0-9]+\.\s.*", line)
    if m:
        initial_tabs = m.group(1)
        n_tabs = len(initial_tabs)
        return n_tabs

    m = re.match(r"(\s+)[0-9]+\.\s.*", line)
    if m:
        initial_spaces = m.group(1)
        n_spaces = len(initial_spaces)
        if n_spaces % 3 == 0:
            return (n_spaces / 3)
        else:
            c_io.log("WRONG # of spaces: %s ('%s')" % (n_spaces, initial_spaces))
            return 0

    c_io.log("NOT AN ORDERED LIST '%s'" % line)
    return 0

def parse_list(c_io):
    el = None

    list_line_re = r"(\s\s\s|\t)+\*\s(.*)"

    line = c_io.next_line()
    if line is None:
        #c_io.log("NOT_A_LIST 1")
        return None
    c_io.unread_line()
    if line.strip() == "":
        #c_io.log("NOT_A_LIST 2")
        return None                     # not a list
    list_level = get_li_level(c_io, line)
    if (list_level is None) or (list_level <= 0):
        #c_io.log("NOT_A_LIST 3")
        c_io.log("not a list '%s'" % line)
        return None                     # not a list

    el = List(level = list_level)

    suspended = 0

    while True:
        line = c_io.next_line()
        if not line:
            break
        line = chomp(line)

        if line.strip() == "":
            # skip empty lines
            suspended += 1
            continue

        m = re.match(list_line_re, line)
        if not m:
            # end of list
            #c_io.unread_line(suspended + 1)
            #suspended = 0
            c_io.unread_line()
            break

        suspended = 0

        assert m
        l_level = get_li_level(c_io, line)
        if l_level > list_level:
            sublist = parse_list(c_io)
            if sublist:
                el.appendChild(ListItem(sublist))
        elif l_level == list_level:
            li = ListItem()
            contents = TWikiConverter(li, m.group(2))
            el.appendChild(li)
        else:
            # end of current list
            c_io.unread_line()
            break

    #c_io.log("GOOD LIST '%s'" % el)
    return el

def parse_ordered_list(c_io):
    el = None

    list_line_re = r"(\s\s\s|\t)+[0-9]+\.\s(.*)"

    line = c_io.next_line()
    if line is None:
        return None
    c_io.unread_line()
    if line.strip() == "":
        return None
    list_level = get_ol_li_level(c_io, line)
    if (list_level is None) or (list_level <= 0):
        c_io.log("not an ordered list '%s'" % line)
        return None                 # not a list

    el = OrderedList(level = list_level)

    suspended = 0

    while True:
        line = c_io.next_line()
        if not line:
            break
        line = chomp(line)

        if line.strip() == "":
            # skip empty lines
            suspended += 1
            continue

        m = re.match(list_line_re, line)
        if not m:
            # end of list
            #c_io.unread_line(suspended + 1)
            #suspended = 0
            c_io.unread_line()
            break

        suspended = 0

        assert m
        l_level = get_ol_li_level(c_io, line)
        if l_level > list_level:
            sublist = parse_ordered_list(c_io)
            if sublist:
                el.appendChild(ListItem(sublist))
        elif l_level == list_level:
            li = ListItem()
            contents = TWikiConverter(li, m.group(2))
            el.appendChild(li)
        else:
            # end of current list
            c_io.unread_line()
            break

    return el


class TWikiConverter(ConverterIO):
    def __init__(self, rootdom, text):
        super(TWikiConverter, self).__init__(rootdom, text)

    def parse(self):
        #self.log("TWikiConverter.parse(%s, '%s')" % (self.rootdom, self.src_text))

        target_el       = None
        in_paragraph    = False
        close_paragraph = False

        remaining = self.src_text
        while remaining:
            #self.log("text:'%s'" % remaining)

            if target_el is None:
                if isinstance(self.rootdom, Document):
                    p_el = Paragraph()
                    self.rootdom.appendChild(p_el)

                    target_el = p_el
                    in_paragraph = True
                else:
                    target_el = self.rootdom

            # a nl ?
            m = re.match(r"^(\s*?)\r?\n(.*)", remaining, re.DOTALL | re.MULTILINE)
            if m:
                (space, remaining) = m.groups()
                contents_el = Text(space + '\n')
                target_el.appendChild(contents_el)
                continue

            # a list ?
            m = re.match(r"\s+\*\s(.*)", remaining)
            if m:
                #self.log("*** list?:'%s'" % remaining)
                c_io = LineIO(remaining)
                ul_el = parse_list(c_io)
                if ul_el:
                    target_el.appendChild(ul_el)
                    remaining = c_io.remaining()
                    continue
                else:
                    #self.log("*** FALSE LIST:'%s'" % remaining)
                    pass

            # an ordered list ?
            m = re.match(r"\s+[0-9]+\.\s(.*)", remaining)
            if m:
                #self.log("ordered list?:'%s'" % remaining)
                c_io = LineIO(remaining)
                ol_el = parse_ordered_list(c_io)
                if ol_el:
                    target_el.appendChild(ol_el)
                    remaining = c_io.remaining()
                    continue
                else:
                    #print "FALSE ORDERED LIST:'%s'" % remaining
                    pass

            m = re.match(r"(?P<leading>.*?)" +
                         r"(?: " +
                         r"(?P<nl> \s*\r?\n )"                                                  + r" | " +
                         r"(?P<meta> \s*%META:[^\n\r]*%\r?\n )"                                 + r" | " +
                         r"(?P<include> \s*%INCLUDE{[^\n\r]*}%\r?\n )"                          + r" | " +
                         r"(?P<verbatim> \s*\<verbatim\>[ ]*\r?\n.*?^\<\/verbatim\>[ ]*\r?\n )" + r" | " +
                         r"(?P<attachlink> \s*\[\[%ATTACHURL%\/[^\]]*\](?:\[[^\]]*\])?\] )"     + r" | " +
                         r"(?P<wikilink> \s*\[\[.*?\](?:\[.*?\])?\] )"                          + r" | " +
                         r"(?P<url> \s*https?://\S+ )"                                          + r" | " +
                         r"(?P<bold> (?=\s?)\*(?=\S)[^,.;\t\n\r]*?(?=\S)\*(?=\s?))"             + r" | " +
                         r"(?P<boldit> (?=\s?)\_\_(?=\S)[^,.;\t\n\r]*?(?=\S)\_\_(?=\s?))"       + r" | " +
                         r"(?P<it> (?=\s?)\_(?=\S)[^,.;\t\n\r]*?(?=\S)\_(?=\s?))"               + r" | " +
                         r"(?P<boldcode> (?=\s?)\=\=(?=\S)[^,.;\t\n\r]*?(?=\S)\=\=(?=\s?))"     + r" | " +
                         r"(?P<code> (?=\s?)\=(?=\S)[^,.;\t\n\r]*?(?=\S)\=(?=\s?))"             + r" | " +
                         r"(?P<br> \%BR\%)"                                                     + r" | " +
                         r"(?P<h1> ^\s*---\+\s+[^\n\r]+\r?\n )"                                 + r" | " +
                         r"(?P<h2> ^\s*---\+\+\s+[^\n\r]+\r?\n )"                               + r" | " +
                         r"(?P<h3> ^\s*---\+\+\+\s+[^\n\r]+\r?\n )"                             + r" | " +
                         r"(?P<h4> ^\s*---\+\+\+\+\s+[^\n\r]+\r?\n )"                           + r" | " +
                         r"(?P<hr> ^\s*---+\s*\r?\n )"
                         r")" +
                         r"(?P<remaining>.*)", remaining, re.DOTALL | re.MULTILINE | re.VERBOSE)
            if m:
                leading   = m.group('leading')
                remaining = m.group('remaining')

                #self.log("lead:'%s'  rem:'%s'  g:%s" % (leading, remaining, m.groups()))
                if leading and (leading != '') and (leading != u''):
                    if isinstance(self.rootdom, Document):
                        p_el_leading = Paragraph(Text(leading))
                    else:
                        p_el_leading = Text(leading)
                    while isinstance(target_el, Paragraph):
                        target_el = target_el.parent
                    if target_el is None:
                        target_el = self.rootdom
                    target_el.appendChild(p_el_leading)
                    #TWikiConverter(p_el_leading, leading)

                contents_el = None

                if m.group('nl'):
                    contents_el = Text(m.group('nl'))
                    close_paragraph = True
                elif m.group('meta'):
                    m2 = re.match(r'%META:([^}]+){(.*)}%', m.group('meta'))
                    if m2:
                        (meta_kw, meta_contents) = m2.groups()
                        if meta_kw.upper() == "TOPICPARENT":
                            pass
                        elif meta_kw.upper() == "TOPICINFO":
                            pass
                        elif meta_kw.upper() == "FILEATTACHMENT":
                            #print "FILEATTACH: %s" % meta_contents
                            pass
                        else:
                            pass
                    else:
                        self.log("WARNING: WRONG META")
                elif m.group('include'):
                    #self.log("INCLUDE")
                    pass
                elif m.group('verbatim'):
                    contents = re.match(r"\s*\<verbatim\>[ ]*\r?\n(.*)^\<\/verbatim\>[ ]*\r?\n", m.group('verbatim'), re.DOTALL | re.MULTILINE).group(1)
                    contents_el = CodeBlock(text = contents)
                elif m.group('url'):
                    #self.log("URL:%s" % m.group('url'))
                    contents = re.match(r"\s*(https?://\S+)", m.group('url')).group(1)
                    contents_el = Link(contents)
                elif m.group('bold'):
                    contents = re.match(r"\*(.*?)\*", m.group('bold')).group(1)
                    contents_el = Strong()
                    TWikiConverter(contents_el, contents)
                elif m.group('it'):
                    contents = re.match(r"\_(.*?)\_", m.group('it')).group(1)
                    contents_el = Emphasis()
                    TWikiConverter(contents_el, contents)
                elif m.group('boldit'):
                    contents = re.match(r"\_\_(.*?)\_\_", m.group('boldit')).group(1)
                    contents_el = EmphasisStrong()
                    TWikiConverter(contents_el, contents)
                elif m.group('boldcode'):
                    contents = re.match(r"\=\=(.*?)\=\=", m.group('boldcode')).group(1)
                    inner_el    = CodeSpan()
                    contents_el = Strong(inner_el)
                    TWikiConverter(inner_el, contents)
                elif m.group('code'):
                    contents = re.match(r"\=(.*?)\=", m.group('code')).group(1)
                    contents_el = CodeSpan()
                    TWikiConverter(contents_el, contents)
                elif m.group('br'):
                    contents_el = LineBreak()
                elif m.group('hr'):
                    contents_el = HR()
                    close_paragraph = True
                elif m.group('h1'):
                    contents = re.match(r"\s*---\+\s+([^\n\r]+)", m.group('h1')).group(1)
                    contents_el = Header(level = 1)
                    TWikiConverter(contents_el, contents)
                    close_paragraph = True
                elif m.group('h2'):
                    contents = re.match(r"\s*---\+\+\s+([^\n\r]+)", m.group('h2')).group(1)
                    contents_el = Header(level = 2)
                    TWikiConverter(contents_el, contents)
                    close_paragraph = True
                elif m.group('h3'):
                    contents = re.match(r"\s*---\+\+\+\s+([^\n\r]+)", m.group('h3')).group(1)
                    contents_el = Header(level = 3)
                    TWikiConverter(contents_el, contents)
                    close_paragraph = True
                elif m.group('h4'):
                    contents = re.match(r"\s*---\+\+\+\+\s+([^\n\r]+)", m.group('h4')).group(1)
                    contents_el = Header(level = 4)
                    TWikiConverter(contents_el, contents)
                    close_paragraph = True
                elif m.group('attachlink'):
                    m2 = re.match(r"\s*\[\[%ATTACHURL%\/(.*?)\]\[(.*?)\]\]", m.group('attachlink'))
                    if m2:
                        (target, desc) = m2.groups()
                    else:
                        m2 = re.match(r"\s*\[\[%ATTACHURL%\/(.*?)\]\]", m.group('attachlink'))
                        (target, desc) = (m2.group(1), None)
                    contents_el = AttachmentLink(target, desc)
                elif m.group('wikilink'):
                    #self.log("WIKIL:%s" % m.group('wikilink'))
                    m2 = re.match(r"\s*\[\[(.*?)\]\[(.*?)\]\]", m.group('wikilink'))
                    if m2:
                        (target, desc) = m2.groups()
                    else:
                        m2 = re.match(r"\s*\[\[(.*?)\]\]", m.group('wikilink'))
                        (target, desc) = (m2.group(1), None)
                    contents_el = WikiLink(target, desc)
                else:
                    print "BAURGH"

                if close_paragraph:
                    if target_el and isinstance(target_el, Paragraph):
                        if (target_el.children is None) or (len(target_el.children) == 0):
                            p = target_el.parent
                            p.removeChild(target_el)
                            in_paragraph    = False
                            close_paragraph = False
                            target_el = p
                        elif len(target_el.children) == 1:
                            cld = target_el.children[0]
                            if isinstance(cld, Text) and (cld.text == '' or cld.text == u''):
                                p = target_el.parent
                                p.removeChild(target_el)
                                in_paragraph    = False
                                close_paragraph = False
                                target_el = p

                if contents_el is not None:
                    target_el.appendChild(contents_el)
                    if close_paragraph:
                        if in_paragraph:
                            in_paragraph = False
                        close_paragraph = False
            else:
                break

        if remaining:
            if isinstance(self.rootdom, Document):
                p_el_tail = Paragraph(Text(remaining))
            else:
                p_el_tail = Text(remaining)
            while isinstance(target_el, Paragraph):
                target_el = target_el.parent
            if target_el is None:
                target_el = self.rootdom
            target_el.appendChild(p_el_tail)
            #contents_el = Text(remaining)
            #target_el.appendChild(contents_el)
            #TWikiConverter(target_el, remaining)

        return self

class Application(object):
    """
    A singleton class implementing the application.
    """

    _instance = None

    def __init__(self, options, args):
        if self._instance:
            raise "An instance of this singleton has already been created."
        Application._instance = self
        self.options = options
        self.args = args

        self.cwd = None			# original working dir
        self.dest_wiki = None           # destination wiki
        self.attachmentdir = None

        self._lines = None
        self._num_lines = 0
        self._next_line = 0

    def Instance(cls):
        return cls._instance
    Instance = classmethod(Instance)

    def log(self, msg, verb=VERBOSITY_VERBOSE):
        if verb <= self.options.verbosity:
            log.info(msg)
        return self

    def dbg(self, msg, verb=VERBOSITY_DEBUG):
        if verb <= self.options.verbosity:
            log.debug(msg)
        return self

    def warn(self, msg):
        m = "WARNING: %s" % msg
        sys.stderr.write("%s\n" % m)
        log.warn(msg)
        return self

    def err(self, msg):
        m = "ERROR: %s" % msg
        sys.stderr.write("%s\n" % m)
        log.error(msg)
        return self

    def Run(self):
        """
        Actual program execution happens here. 
        """
        from softwarefabrica.django.wiki.models import Wiki, Page, PageContent, Attachment

        self.log("Program started.")

        if self.options.attachmentdir:
            self.attachmentdir = self.options.attachmentdir
        else:
            basedir = os.path.dirname(os.path.dirname(self.options.inputdir))
            wikinamedir = os.path.basename(self.options.inputdir)
            self.attachmentdir = os.path.join(os.path.join(os.path.join(basedir, 'www'), 'pub'), wikinamedir)

        try:
            dest_wiki = Wiki.objects.get(fullname_cache = self.options.targetwiki)
        except ObjectDoesNotExist:
            # TODO: handle qualified names, searching for parent, determining final name component, and so on...
            dest_wiki = Wiki(name = self.options.targetwiki)
            dest_wiki.save()
        self.dest_wiki = dest_wiki

        self.log("Destination wiki: %s" % self.dest_wiki)

        self.cwd = os.getcwd()

        filenames = glob.glob(os.path.join(self.options.inputdir, "*.txt"))
        for filename in filenames:
            self.convert_twiki(filename)

        os.chdir(self.cwd)
        self.log("Program terminating...")
        return self

    def convert_twiki(self, filename):
        from django.conf import settings
        from softwarefabrica.django.wiki.models import Wiki, Page, PageContent, Attachment

        self.log("PROCESSING '%s'" % filename)

        basename = os.path.basename(filename)
        if basename in SKIP_TWIKI_FILES:
            return

        m = re.match(r'(.*)\.txt', basename)
        if m:
            pagename = m.group(1)
        else:
            pagename = basename

        fh = open(filename, 'r')
        txt = fh.read()
        fh.close()

        # convert encoding
        txt = unicode(txt, 'iso-8859-1')

        # scan for attachments
        attachments = []
        attachments_by_name = {}
        meta_re = re.compile(r"^%META:([^\r\n]+)%\r?\n", re.DOTALL | re.MULTILINE | re.VERBOSE)
        for m in re.finditer(meta_re, txt):
            meta_inner = m.group(1)
            m2 = re.match(r'([^{}]*){(.*)}', meta_inner)
            if m2:
                (meta_kw, meta_opts) = m2.groups()
                if meta_kw.upper() == 'FILEATTACHMENT':
                    opt_re = re.compile(r'\s*([a-zA-Z0-9_]+)\s*=\s*\"(.*?)\"')
                    opts = {}
                    for m3 in re.finditer(opt_re, meta_opts):
                        (opt_name, opt_value) = m3.groups()
                        if opt_value.startswith('"'):
                            opt_value = opt_value[1:-1]
                        opts[opt_name] = opt_value
                    #print "attachment:%s" % opts
                    attachments.append(opts)
                    attachments_by_name[opts['name']] = opts

        dom  = Document()
        cvt  = TWikiConverter(dom, txt)
        mdwn = dom.Perform(operation_generate_markdown)
        #self.log(u"converted:%s" % cvt)
        #self.log("markdown: %s" % str(mdwn))

        ## encode in utf8
        #mdwn = unicode(mdwn, 'utf_8', errors='replace')

        page        = None
        old_content = None
        content     = None

        page_exists = False
        try:
            page = Page.objects.get(wiki = self.dest_wiki, fullname_cache = pagename)
            page_exists = True
            old_content = page.get_content()
        except ObjectDoesNotExist:
            page = Page(wiki = self.dest_wiki, name = pagename)
            page.save()
            old_content = None

        for att in attachments:
            if not 'name' in att:
                continue
            att_name = att['name']
            att_path = att['path']
            src_shortpath = att['name']
            src_fname     = os.path.basename(src_shortpath)
            src_dirname   = os.path.join(self.attachmentdir, page.name)
            src_pathname  = os.path.join(src_dirname, src_fname)

            desc = att_name
            if 'comment' in att:
                desc = att['comment']
            #print "ATTACHMENT %s path:%s" % (att_name, src_shortpath)
            from django.core.files import File

            dst_relpath  = page_attachment_upload_to(page, src_fname)
            dst_pathname = os.path.join(settings.MEDIA_ROOT, dst_relpath)
            dst_dirname  = os.path.dirname(dst_pathname)

            #os.system("cp -a %s %s" % (src_pathname, dst_pathname))

            att_obj = Attachment(page = page, name = att_name, desc = desc, attachment = "CIAO")
            att_obj.save()

            src_fh = open(src_pathname, 'rb')
            att_obj.attachment.save(src_fname, File(src_fh))
            src_fh.close()

            att['obj'] = att_obj
            att['url'] = att_obj.attachment.url

        if self.options.overwrite or (not page_exists) or (old_content is None):
            content = PageContent(page = page, title = pagename, text = mdwn)
            content.linked.clear()

            if old_content:
                content.uuid    = None
                content.created = None
                content.rev = old_content.rev + 1
            if (old_content is None) or (not content.same_content(old_content)):
                content.save()

        return cvt

def exithandler(signum, frame):
    """
    Handles (gracefully) termination signals.
    """

    app = Application.Instance()

    log.info('Exiting with signal %s' % signum)

    # handle graceful exit

    log.info("exiting.")
    sys.exit(1)

#============================================================================#
# main - program entry point
#============================================================================#

def _test():
    """
    Test entry point
    """
    import doctest
    doctest.testmod()

def set_django_settings(settings_module):
    if os.path.exists(settings_module) and os.path.isdir(settings_module):
        DJANGO_SETTINGS_MODULE = settings_module + '.settings'
    else:
        DJANGO_SETTINGS_MODULE = settings_module
    os.environ['DJANGO_SETTINGS_MODULE'] = DJANGO_SETTINGS_MODULE
    return True

def main():
    """
    Program entry point
    """

    parser = optparse.OptionParser( version = "softwarefabrica TWiki wiki import tool (%%prog) version %s (lib. %s)" % (__version__, version.get_version()),
                                    usage = """%prog [options]

Import a TWiki wiki into a softwarefabrica wiki.
""" )

    parser.add_option( "-s", "--settings",
                       help = "specify SETTINGS as the django settings module",
                       action = "store", dest = "django_settings",
                       default = "", metavar = "SETTINGS" )
    parser.add_option( "-i", "--input-dir",
                       help = "specify INPUTDIR as the input directory (default: %s)" % repr(DEFAULT_INPUT_DIR),
                       action = "store", dest = "inputdir",
                       default = DEFAULT_INPUT_DIR, metavar = "INPUTDIR" )
    parser.add_option( "-a", "--attachment-dir",
                       help = "specify ATTACHMENTDIR as the input attachment directory (default: determined)",
                       action = "store", dest = "attachmentdir",
                       default = None, metavar = "ATTACHMENTDIR" )
    parser.add_option( "-t", "--target", "--target-wiki",
                       help = "specify WIKI as the destination wiki (default: %s)" % repr(DEFAULT_TARGET_WIKI),
                       action = "store", dest = "targetwiki",
                       default = DEFAULT_TARGET_WIKI, metavar = "WIKI" )
    parser.add_option( "-o", "--overwrite",
                       help = "force overwrite of existing pages",
                       action = "store_true", dest = "overwrite", default = False )
    parser.add_option("-q", "--quiet",
                      action="store_const", dest="verbosity", const=VERBOSITY_QUIET, default=VERBOSITY_NORMAL,
                      help="don't print anything on stdout" )
    parser.add_option("-v", "--verbose",
                      action="store_const", dest="verbosity", const=VERBOSITY_VERBOSE,
                      help="be verbose" )
    parser.add_option("-d", "--debug",
                      action="store_const", dest="verbosity", const=VERBOSITY_DEBUG,
                      help="be too verbose (debugging only)" )
    parser.add_option("--test", help = "perform internal testing.",
                       action = "store_true", dest = "test", default = False )

    options, args = parser.parse_args( sys.argv )

    if options.test:
        _test()
        sys.exit()

    import logging.config

    #logging.basicConfig()
    logging.config.fileConfig(LOGGING_CONF_FILE)
    log.info('Starting %s...' % PROGNAME)

    unixsignal.signal(unixsignal.SIGINT,  exithandler)
    try:
        unixsignal.signal(unixsignal.SIGQUIT, exithandler)
    except:
        pass
    try:
        unixsignal.signal(unixsignal.SIGTERM, exithandler)
    except:
        pass
    try:
        unixsignal.signal(unixsignal.SIGKILL, exithandler)
    except:
        pass

    if options.django_settings:
        set_django_settings(options.django_settings)

    if not check_django_settings():
        sys.stderr.write("ERROR: django settings not available.\n")
        sys.exit(1)

    if not options.inputdir:
        sys.stderr.write("ERROR: specify the input directory\n")
        sys.exit(1)

    if not os.path.exists(options.inputdir):
        sys.stderr.write("ERROR: the input directory '%s' doesn't exist\n" % options.inputdir)
        sys.exit(1)

    app = Application(options, args)
    app.Run()
    return 0                            # make setuptools application wrapper happy

if __name__ == '__main__':
    main()
