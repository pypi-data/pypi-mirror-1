# models.py
#
# Copyright (C) 2008 Marco Pantaleoni. All rights reserved
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

from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from django.contrib.auth.models import User
from softwarefabrica.django.utils.UUIDField import UUIDField

import datetime

PARENT_SEPARATOR         = u"|"         # u"/"
URL_PARENT_SEPARATOR     = u"|"
WIKI_PAGE_SEPARATOR      = u"."
URL_WIKI_PAGE_SEPARATOR  = u"."

class Wiki(models.Model):
    uuid        = UUIDField(_("uuid"), primary_key=True, db_index=True)
    parent      = models.ForeignKey('self', db_index=True, verbose_name=_("parent"), related_name='wiki_parent_set', blank=True, null=True)
    name	= models.CharField(_("name"), max_length=40, blank=False, db_index=True)
    desc	= models.CharField(_("description"), max_length = 200, blank = True)
    long_desc	= models.TextField(_("long description"), blank=True)

    publish      = models.BooleanField(_("publish"),   default=True, db_index=True, blank=True)
    publish_from = models.DateField(_("publish from"), db_index=True, blank=True, null=True)
    publish_to   = models.DateField(_("publish to"),   db_index=True, blank=True, null=True)

    homepage    = models.ForeignKey('Page', db_index=True, verbose_name=_("home page"), related_name='homepage_wiki_set', blank = True, null = True)

    author      = models.ForeignKey(User, db_index=True, verbose_name=_("author"), related_name='author_wiki_set', blank = True, null = True, editable=False)
    modifiedby  = models.ForeignKey(User, db_index=True, verbose_name=_("modified by"), related_name='modifiedby_wiki_set', blank = True, null = True, editable=False)
    created     = models.DateTimeField(_("created"), db_index=True, editable=False)
    modified    = models.DateTimeField(_("modified"), db_index=True, editable=False)

    fullname_cache     = models.CharField(_("fullname_cache"), max_length=200, blank=False, db_index=True, editable=False)
    fullname_url_cache = models.CharField(_("fullname_url_cache"), max_length=200, blank=False, db_index=True, editable=False)

    class Meta:
        unique_together = (('parent', 'name'), ('parent', 'fullname_cache'), ('parent', 'fullname_url_cache'),)

    def __unicode__(self):
        return self.get_full_name()

    def save(self):
        fullname     = self.get_full_name()
        fullname_url = self.get_full_name(separator = URL_PARENT_SEPARATOR)
        self.fullname_cache     = fullname
        self.fullname_url_cache = fullname_url

        time_now = datetime.datetime.now()
        if not self.created:
            self.created = time_now
        self.modified = time_now
        return_value = super(Wiki, self).save()
        return return_value

    def get_absolute_url(self):
        return ('wiki-page-list', (), {'wikiname': self.fullname_url})
    get_absolute_url = permalink(get_absolute_url)

    def get_full_name(self, separator=PARENT_SEPARATOR):
        """
        Return the full name for this object, complete with pieces from its ancestors.
        For example: 'Recipes/Cookies'.
        """
        if self.parent is not None:
            return u"%s%s%s" % (self.parent.get_full_name(separator = separator), separator, self.name)
        return self.name

    def get_full_name_url(self):
        return self.get_full_name(separator = URL_PARENT_SEPARATOR)

    fullname     = property(get_full_name, None, None, "wiki full name")
    fullname_url = property(get_full_name_url, None, None, "wiki full name for URLs")

    get_absolute_name     = get_full_name
    get_absolute_name_url = get_full_name_url

    absolutename     = property(get_absolute_name, None, None, "wiki absolute name")
    absolutename_url = property(get_absolute_name_url, None, None, "wiki absolute name for URLs")

    def ancestors(self, include_self=False):
        ancestors = []
        if include_self:
            ancestors.append(self)
        p = self.parent
        while p:
            ancestors.append(p)
            p = p.parent
        return ancestors

    def ancestors_with_self(self):
        return self.ancestors(include_self = True)

class Page(models.Model):
    uuid        = UUIDField(_("uuid"), primary_key=True, db_index=True)
    parent      = models.ForeignKey('self', db_index=True, verbose_name=_("parent"), related_name='page_parent_set', blank=True, null=True)
    wiki	= models.ForeignKey(Wiki, db_index=True, verbose_name=_("wiki"), related_name='wiki_page_set', blank=False, null=False)
    name	= models.CharField(_("name"), max_length=40, blank=False, db_index=True)
    desc	= models.CharField(_("description"), max_length = 200, blank = True)

    up		= models.ForeignKey('self', db_index=True, verbose_name=_("up"), related_name='page_child_set', blank=True, null=True)
    prev	= models.ForeignKey('self', db_index=True, verbose_name=_("previous"), related_name='page_next_set', blank=True, null=True)
    next	= models.ForeignKey('self', db_index=True, verbose_name=_("next"), related_name='page_prev_set', blank=True, null=True)

    publish      = models.BooleanField(_("publish"),   default=True, db_index=True, blank=True)
    publish_from = models.DateField(_("publish from"), db_index=True, blank=True, null=True)
    publish_to   = models.DateField(_("publish to"),   db_index=True, blank=True, null=True)

    author      = models.ForeignKey(User, db_index=True, verbose_name=_("author"), related_name='author_page_set', blank = True, null = True, editable=False)
    modifiedby  = models.ForeignKey(User, db_index=True, verbose_name=_("modified by"), related_name='modifiedby_page_set', blank = True, null = True, editable=False)
    created     = models.DateTimeField(_("created"), db_index=True, editable=False)
    modified    = models.DateTimeField(_("modified"), db_index=True, editable=False)

    fullname_cache     = models.CharField(_("fullname_cache"), max_length=200, blank=False, db_index=True, editable=False)
    fullname_url_cache = models.CharField(_("fullname_url_cache"), max_length=200, blank=False, db_index=True, editable=False)

    class Meta:
        unique_together = (('wiki', 'parent', 'name'), ('wiki', 'parent', 'fullname_cache'), ('wiki', 'parent', 'fullname_url_cache'),)

    def __unicode__(self):
        return self.name

    def save(self, recurse=True):
        fullname     = self.get_full_name()
        fullname_url = self.get_full_name(separator = URL_PARENT_SEPARATOR)
        self.fullname_cache     = fullname
        self.fullname_url_cache = fullname_url

        time_now = datetime.datetime.now()
        if not self.created:
            self.created = time_now
        self.modified = time_now
        if recurse:
            if self.prev and self.prev.next != self:
                self.prev.next = self
                self.prev.save(recurse = False)
            if self.next and self.next.prev != self:
                self.next.prev = self
                self.next.save(recurse = False)
        return_value = super(Page, self).save()
        return return_value

    def get_absolute_url(self):
        return ('wiki-page-detail', (), {'wikiname': self.wiki.fullname_url, 'pagename': self.name})
    get_absolute_url = permalink(get_absolute_url)

    def get_content(self, rev=None):
        if rev is not None:
            contents = self.pagecontent_set.filter(rev = rev).order_by('-rev', '-modified', '-created')
            if contents.count() > 0:
                return contents[0]
            return None
        contents = self.pagecontent_set.order_by('-rev', '-modified', '-created')
        if contents.count() > 0:
            return contents[0]
        return None

    def get_full_name(self, separator=PARENT_SEPARATOR):
        """
        Return the full name for this object, complete with pieces from its ancestors.
        For example: 'Personal/Bank'.
        """
        return self.name

    def get_full_name_url(self):
        return self.get_full_name(separator = URL_PARENT_SEPARATOR)

    fullname     = property(get_full_name, None, None, "page full name")
    fullname_url = property(get_full_name_url, None, None, "page full name for URLs")

    def get_absolute_name(self, wiki_separator=PARENT_SEPARATOR, page_separator=PARENT_SEPARATOR, separator=WIKI_PAGE_SEPARATOR):
        """
        Return the absolute name for this object, complete with pieces from its ancestors
        and the full name of its wiki.
        For example: 'Misc.Personal/Bank'.
        """
        return u"%s%s%s" % (self.wiki.get_full_name(separator = wiki_separator), separator, self.get_full_name(separator = page_separator))

    def get_absolute_name_url(self):
        return self.get_absolute_name(wiki_separator = URL_PARENT_SEPARATOR, page_separator = URL_PARENT_SEPARATOR, separator = URL_WIKI_PAGE_SEPARATOR)

    absolutename     = property(get_absolute_name, None, None, "page absolute name")
    absolutename_url = property(get_absolute_name_url, None, None, "page absolute name for URLs")

    def ancestors(self, include_self=False):
        ancestors = []
        if include_self:
            ancestors.append(self)
        p = self.parent
        while p:
            ancestors.append(p)
            p = p.parent
        return ancestors

    def ancestors_with_self(self):
        return self.ancestors(include_self = True)

class PageContent(models.Model):
    uuid        = UUIDField(_("uuid"), primary_key=True, db_index=True)
    page	= models.ForeignKey(Page, db_index=True, verbose_name=_("page"), related_name='pagecontent_set', blank=False, null=False)
    rev         = models.PositiveIntegerField(_("revision"), blank=False, default=1, db_index=True, editable=False)
    title       = models.CharField(_("title"), max_length = 220, blank = True)
    text	= models.TextField(_("text"), blank=True)
    text_html	= models.TextField(_("HTML"), blank=True, editable=False)

    references  = models.ManyToManyField(Page, db_index=True, verbose_name=_("referenced pages"), related_name="referencedby", null=True, blank=True)
    linked      = models.ManyToManyField(Page, db_index=True, verbose_name=_("linked pages"), related_name="linkedby", null=True, blank=True, editable=False)

    author      = models.ForeignKey(User, db_index=True, verbose_name=_("author"), related_name='author_pagecontent_set', blank = True, null = True, editable=False)
    modifiedby  = models.ForeignKey(User, db_index=True, verbose_name=_("modified by"), related_name='modifiedby_pagecontent_set', blank = True, null = True, editable=False)
    created     = models.DateTimeField(_("created"), db_index=True, editable=False)
    modified    = models.DateTimeField(_("modified"), db_index=True, editable=False)

    def __unicode__(self):
        return u"%s - r%s" % (self.page, self.rev)

    def save(self):
        o_uuid = self.uuid
        import wikiparse
        (text_html, linked_pages) = wikiparse.wikiparse(self)
        self.text_html = text_html
        if o_uuid is not None:
            self.linked = linked_pages
        time_now = datetime.datetime.now()
        if not self.created:
            self.created = time_now
        self.modified = time_now
        return_value = super(PageContent, self).save()
        if self.uuid and (o_uuid is None):
            self.linked = linked_pages
            return_value = super(PageContent, self).save()
        # HACK: this seems necessary for some strange reason
        #       otherwise when saving from outside form processing
        #       the m2m are not saved
        self.linked = linked_pages
        #for p in linked_pages:
        #    self.linked.add(p)
        return return_value

    def same_content(self, other_pagecontent):
        if other_pagecontent is None:
            return False
        return (self.title == other_pagecontent.title) and (self.text == other_pagecontent.text)

    def get_wiki(self):
        return self.page.wiki

    wiki = property(get_wiki, None, None, "PageContent wiki")

def page_attachment_upload_to(instance, filename):
    # WARNING: the attachment filesystem path should NOT contain
    # any reference to the wiki name or the page name, in order
    # to ease renames.
    #page_absolute_name = instance.page.get_absolute_name()
    #page_absolute_name_fs = page_absolute_name.replace("/", "_").replace(".", "/")
    attachment_instance = instance
    page_instance = instance.page
    print "page_attachment_upload_to(instance:%s, filename:%s)" % (instance, filename)
    time_now = datetime.datetime.now()
    upload_to = ("page-%s" % page_instance.uuid) + "/" + time_now.strftime("%Y%m%d") + "/" + filename
    #upload_to = page_absolute_name_fs + "/" + time_now.strftime("%Y%m%d") + "/" + filename
    return upload_to

class Attachment(models.Model):
    uuid        = UUIDField(_("uuid"), primary_key=True, db_index=True)
    page	= models.ForeignKey(Page, db_index=True, verbose_name=_("page"), related_name='attachment_set', blank=False, null=False)
    name	= models.CharField(_("name"), max_length=40, blank=False, db_index=True)
    desc	= models.CharField(_("description"), max_length = 200, blank = True)

    attachment  = models.FileField(_("attachment"),
                                   upload_to = page_attachment_upload_to,
                                   max_length = 200)

    author      = models.ForeignKey(User, db_index=True, verbose_name=_("author"), related_name='author_attachment_set', blank = True, null = True, editable=False)
    modifiedby  = models.ForeignKey(User, db_index=True, verbose_name=_("modified by"), related_name='modifiedby_attachment_set', blank = True, null = True, editable=False)
    created     = models.DateTimeField(_("created"), db_index=True, editable=False)
    modified    = models.DateTimeField(_("modified"), db_index=True, editable=False)

    class Meta:
        unique_together = (('page', 'name'),)

    def __unicode__(self):
        return u"%s - %s" % (self.page, self.name)

    def save(self):
        time_now = datetime.datetime.now()
        if not self.created:
            self.created = time_now
        self.modified = time_now
        return_value = super(Attachment, self).save()
        return return_value

from django.contrib import admin

admin.site.register(Wiki)
admin.site.register(Page)
admin.site.register(PageContent)
admin.site.register(Attachment)
