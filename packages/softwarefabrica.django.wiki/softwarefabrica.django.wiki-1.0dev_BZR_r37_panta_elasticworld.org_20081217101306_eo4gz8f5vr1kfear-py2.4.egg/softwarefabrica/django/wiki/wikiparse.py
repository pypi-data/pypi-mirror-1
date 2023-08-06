# wikiparse.py - wiki parser
#
# Copyright (C) 2006-2008 Marco Pantaleoni. All rights reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from django import template
from django.conf import settings
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
import re

from softwarefabrica.django.wiki.models import *
from softwarefabrica.django.wiki.sanitize import sanitize_html

class WikiParser(object):
    def __init__(self, pagecontent, src_text,
                 do_html_sanitization=False,
                 mdwn_extensions=['footnotes', 'tables',]):
        self.pagecontent = pagecontent
        self.page        = pagecontent.page
        self.wiki        = None
        if self.page:
            self.wiki    = self.page.wiki

        self.src_text    = src_text
        self.do_html_sanitization = do_html_sanitization

        self.mdwn_extensions = mdwn_extensions

        self.parsed             = mark_safe(u"")
        self.linked_pages       = []
        self.linked_attachments = []

    def parse(self):
        text = self.src_text

        # step 1. sanitize html
        if self.do_html_sanitization:
            text = sanitize_html(text)

        # step 2. encode in utf8
        #value = value.encode('utf8', 'replace')
        #if type(value) != type(u''):
        #    value = unicode(value, 'utf-8', errors='replace')
        text = force_unicode(text)

        text = self.pre_parse(text)
        text = self.markup_parse(text)
        text = self.post_parse(text)

        self.parsed = mark_safe(text)
        return (self.parsed, self.linked_pages)

    def pre_parse(self, text):
        text = self.parse_wiki_tags(text)
        return text

    def markup_parse(self, text):
        try:
            import markdown
        except ImportError:
            if settings.DEBUG:
                raise template.TemplateSyntaxError, "Error in {% wiki %} filter: The Python markdown library isn't installed."
            return force_unicode(text)

        makesafe = False

        if hasattr(markdown, 'logger'):
            import logging
            markdown.logger.setLevel(logging.WARN)

        # markdown.version was first added in 1.6b. The only version of markdown
        # to fully support extensions before 1.6b was the shortlived 1.6a.
        if hasattr(markdown, 'version'):
    ##        extensions = [e for e in arg.split(",") if e]
    ##        if len(extensions) > 0 and extensions[0] == "safe":
    ##            extensions = extensions[1:]
    ##            safe_mode = True
    ##        else:
    ##            safe_mode = False
            extensions = self.mdwn_extensions or ['footnotes', 'tables',]

            if makesafe:
                safe_mode = 'escape'        # 'replace' (default) or 'escape'
            else:
                safe_mode = False

            # Unicode support only in markdown v1.7 or above. Version_info
            # exist only in markdown v1.6.2rc-2 or above.
            if getattr(markdown, "version_info", None) < (1,7):
                mdwn = mark_safe(force_unicode(markdown.markdown(smart_str(text), extensions, extension_configs = extension_configs, safe_mode=safe_mode)))
            else:
                md = markdown.Markdown(force_unicode(text),
                                       extensions = extensions,
                                       #extension_configs = extension_configs,
                                       #encoding = 'utf8',
                                       safe_mode = safe_mode)
                mdwn = mark_safe(unicode(md))
                #mdwn = mark_safe(markdown.markdown(force_unicode(text), extensions, extension_configs = extension_configs, safe_mode=safe_mode))
        else:
            mdwn = mark_safe(force_unicode(markdown.markdown(smart_str(text))))
        return mdwn

    def post_parse(self, text):
        #text = self.parse_wiki_tags(text)
        return text

    def parse_wiki_tags(self, text):
        wikiname = 'Home'
        wiki = None
        if self.page:
            wiki     = self.page.wiki
            wikiname = wiki.name

        self.linked_pages       = []
        self.linked_attachments = []

        if text is None:
            return mark_safe("")
        if (text == "") or (text == u""):
            return mark_safe(text)

        parsed    = u""
        remaining = text
        while remaining:
            m = re.match(r'(?P<leading>.*?) (?:' +
#                         '(?P<url> [A-Za-z\+]+://[A-Za-z0-9-_%&\@\?\/.=]+)' + ' | ' +
                         '(?P<mdwn_link> \[[A-Za-z0-9_\+ \t]+\]\([A-Za-z0-9:\/-_%&\@\?.=]+\))' + ' | ' +
                         '(?P<mdwn_img> \!\[[A-Za-z0-9_\+ \t]+\]\([A-Za-z0-9:\/-_%&\@\?.= \t\"]+\))' + ' | ' +
                         '(?P<mdwn_img_ref> \!\[[A-Za-z0-9_\+ \t]+\]\[[A-Za-z0-9:\/-_%&\@\?.= \t\"]+\])' + ' | ' +
                         '(?P<wikiword> [A-Z][a-z]+[A-Z][a-zA-Z0-9_]+)' + ' | ' +
                         '(?P<attachmentlink> \[\[attachment:[^\]\|]+(?:\|[^\]]+)?\]\])' + ' | ' +
                         '(?P<wikilink> \[\[[^\]\|]+(?:\|[^\]]+)?\]\])' +
                         ' ) (?P<remaining>.*)',
                         remaining, re.MULTILINE | re.VERBOSE | re.DOTALL)

            if m:
                leading   = m.group('leading')
                remaining = m.group('remaining')

                parsed += leading

#                 if m.group('url'):
#                     url_text = m.group('url')

#                     linktitle = url_text
#                     if linktitle:
#                         a_title_str = ' title="%s"' % linktitle
#                     else:
#                         a_title_str = ' title="%s"' % url_text

#                     url  = url_text
#                     desc = url_text
#                     link = r'<span class="extlink"><a href="%s"%s>%s</a></span>' % (url, a_title_str, linktitle)
#                     print "LINK:%s" % repr(link)
#                     if link:
#                         parsed += link
		if m.group('mdwn_link'):
                    mdwn_text = m.group('mdwn_link')
                    parsed += mdwn_text
                elif m.group('mdwn_img'):
                    mdwn_text = m.group('mdwn_img')
                    print "mdwn_img:%s" % mdwn_text
                    parsed += mdwn_text
                elif m.group('mdwn_img_ref'):
                    mdwn_text = m.group('mdwn_img_ref')
                    print "mdwn_img_ref:%s" % mdwn_text
                    parsed += mdwn_text
                elif m.group('wikiword'):
                    wikiword = m.group('wikiword')

                    link     = None
                    wikipage = None
                    try:
                        wikipage = Page.objects.get(name = wikiword)
                        self.linked_pages.append(wikipage)
                    except ObjectDoesNotExist:
                        pass

                    if wikipage:
                        url  = wikipage.get_absolute_url()
                        desc = wikipage.desc
                        a_class = 'wikipresent'
                    else:
                        url  = reverse('wiki-page-create-named', kwargs={'wikiname': wikiname, 'pagename': wikiword})
                        desc = ''
                        a_class = 'wikinotpresent'
                    a_class_str = ''
                    if a_class:
                        a_class_str = ' class="%s"' % a_class
                    link = r'<a href="%s"%s>%s</a>' % (url, a_class_str, wikiword)

                    if link:
                        parsed += link
                elif m.group('attachmentlink'):
                    attlink = m.group('attachmentlink')
                    (attname, linktitle) = re.match(r"\[\[attachment:(?P<attname>[^\]\|]+)(?:\|(?P<atttitle>[^\]]+))?\]\]", attlink).groups()

                    if attname and re.match(r'".*"', attname):
                        attname = attname[1:-1]
                    if linktitle and re.match(r'".*"', linktitle):
                        linktitle = linktitle[1:-1]
                    if linktitle:
                        linktitle = sanitize_html(linktitle, valid_tags='', valid_attrs='')
                    if linktitle:
                        linktitle = re.sub(r'\`', "", linktitle, 0)

                    l_wikiname = wikiname
                    l_pagename = self.page.fullname_cache
                    l_attname  = attname
                    if ('/' in attname):
                        comps = attname.split('/')
                        if len(comps) >= 3:
                            (l_wikiname, l_pagename, l_attname) = comps
                        elif len(comps) == 2:
                            (l_pagename, l_attname) = comps
                        elif len(comps) == 1:
                            (l_attname,) = comps

                    link      = None
                    attachment = None

                    if l_wikiname:
                        try:
                            l_wiki = Wiki.objects.get(fullname_cache = l_wikiname)
                        except ObjectDoesNotExist:
                            l_wiki = wiki
                    else:
                        l_wikiname = wikiname
                        l_wiki = wiki

                    if l_pagename:
                        try:
                            l_page = Page.objects.get(wiki = l_wiki, fullname_cache = l_pagename)
                        except ObjectDoesNotExist:
                            l_page = self.page
                    else:
                        l_pagename = self.page.fullname_cache
                        l_page     = self.page

                    try:
                        attachment = Attachment.objects.get(page = l_page, name = l_attname)
                        self.linked_attachments.append(attachment)
                    except ObjectDoesNotExist:
                        pass

                    if linktitle:
                        a_title_str = ' title="%s %s"' % (l_attname, linktitle)
                    else:
                        a_title_str = ' title="%s %s"' % (l_attname, ("%s.%s" % (l_wikiname, l_pagename)))

                    if attachment:
                        url  = attachment.attachment.url
                        desc = attachment.desc
                        a_class = 'wikipresent'
                    else:
                        url  = reverse('wiki-attachment-create-named', kwargs={'wikiname': l_wikiname, 'pagename': l_pagename, 'attachmentname': l_attname})
                        desc = ''
                        a_class = 'wikinotpresent'
                    a_class_str = ''
                    if a_class:
                        a_class_str = ' class="%s"' % a_class
                    if attachment:
                        link = r'<a href="%s"%s%s>%s</a></span>' % (url, a_class_str, a_title_str, linktitle)
                    else:
                        link = r'<a href="%s"%s%s>%s</a></span>' % (url, a_class_str, a_title_str, l_attname)

                    if link:
                        parsed += link
                elif m.group('wikilink'):
                    wlink = m.group('wikilink')
                    (wikiword, linktitle) = re.match(r"\[\[(?P<wikiword>[^\]\|]+)(?:\|(?P<wikititle>[^\]]+))?\]\]", wlink).groups()

                    if linktitle and re.match(r'".*"', linktitle):
                        linktitle = linktitle[1:-1]
                    if linktitle:
                        linktitle = sanitize_html(linktitle, valid_tags='', valid_attrs='')
                    if linktitle:
                        linktitle = re.sub(r'\`', "", linktitle, 0)

                    l_wikiname = None
                    l_pagename = wikiword
                    l_external = False
                    if (wikiword.startswith('http://') or
                        wikiword.startswith('https://') or
                        wikiword.startswith('ftp://') or
                        wikiword.startswith('ftps://') or
                        wikiword.startswith('svn://') or
                        wikiword.startswith('bzr://') or
                        wikiword.startswith('sftp://') or
                        wikiword.startswith('bzr+sftp://')):
                        l_external = True
                    elif ('.' in wikiword) and (len(wikiword.split('.')) > 2):
                        pass
                    elif '.' in wikiword:
                        (l_wikiname, l_pagename) = wikiword.split('.')

                    link     = None
                    wikipage = None

                    if l_wikiname:
                        try:
                            l_wiki = Wiki.objects.get(fullname_cache = l_wikiname)
                        except ObjectDoesNotExist:
                            l_wiki = wiki
                    else:
                        l_wikiname = wikiname
                        l_wiki = wiki

                    try:
                        wikipage = Page.objects.get(wiki = l_wiki, fullname_cache = l_pagename)
                        self.linked_pages.append(wikipage)
                    except ObjectDoesNotExist:
                        pass

                    if not linktitle:
                        if wikipage:
                            linktitle = wikipage.desc or wikiword
                        else:
                            linktitle = wikiword
                    if wikipage:
                        a_title_str = ' title="%s [[%s]]"' % (wikipage.desc or linktitle or wikiword, wikipage.absolutename)
                    else:
                        a_title_str = ' title="%s [[%s]]"' % (linktitle or ("%s.%s" % (l_wikiname, l_pagename)), wikiword)

                    if l_external:
                        url  = l_pagename
                        a_class = 'external'
                        linktext = url
                    else:
                        if wikipage:
                            url  = wikipage.get_absolute_url()
                            desc = wikipage.desc or wikiword
                            linktext = linktitle or wikipage.desc or wikiword
                            a_class = 'wikipresent'
                        else:
                            url  = reverse('wiki-page-create-named', kwargs={'wikiname': wikiname, 'pagename': l_pagename})
                            desc = ''
                            linktext = linktitle or wikiword
                            a_class = 'wikinotpresent'
                    a_class_str = ''
                    if a_class:
                        a_class_str = ' class="%s"' % a_class
                    link = r'<a href="%s"%s%s>%s</a>' % (url, a_class_str, a_title_str, linktext)

                    if link:
                        parsed += link
            else:
                break
        if remaining:
            parsed += remaining

        return mark_safe(parsed)

def wikiparse(pagecontent, makesafe=True):
    page = pagecontent.page

    value = pagecontent.text

    parser = WikiParser(pagecontent, value)
    return parser.parse()
