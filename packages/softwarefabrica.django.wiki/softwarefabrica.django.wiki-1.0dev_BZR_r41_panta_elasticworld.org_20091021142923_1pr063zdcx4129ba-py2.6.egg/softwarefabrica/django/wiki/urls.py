from django.conf.urls.defaults import *
from django.conf import settings

from softwarefabrica.django.crud.crud import *

from softwarefabrica.django.wiki.models import *
from softwarefabrica.django.wiki.views import v_wikipage, v_wikipage_edit, v_search

wiki_list = ListObjectView(queryset = Wiki.objects.all(),
                           paginate_by = 10,
                           allow_empty = True,
                           template_name = "wiki/wiki_list.html")

wiki_create = CreateObjectView(model = Wiki, template_name = "wiki/wiki_edit.html")

def wiki_edit(request, wikiname, **kwargs):
    wiki = Wiki.objects.get(fullname_url_cache__exact = wikiname)
    return update_object(request, model= Wiki, object_id = wiki.uuid,
                         extra_context = { 'wiki': wiki },
                         template_name = "wiki/wiki_edit.html",
                         **kwargs)

def wiki_page_list(request, wikiname, **kwargs):
    wiki = Wiki.objects.get(fullname_url_cache__exact = wikiname)
    wiki_pages = Page.objects.filter(wiki = wiki)
    return object_list(request, queryset = wiki_pages,
                       extra_context = { 'wiki': wiki },
                       paginate_by = 20,
                       allow_empty = True,
                       template_name = "wiki/page_list.html",
                       **kwargs)

def wikipage_history(request, wikiname, pagename, **kwargs):
    wiki = Wiki.objects.get(fullname_url_cache__exact = wikiname)
    page = Page.objects.get(wiki = wiki, name__exact = pagename)
    contents = PageContent.objects.filter(page = page).order_by('-rev')
    return object_list(request, queryset = contents,
                       extra_context = { 'wiki': wiki, 'name': page.name, 'wpage': page, 'content': page.get_content(), },
                       paginate_by = 20,
                       allow_empty = True,
                       template_name = "wiki/page_history.html",
                       **kwargs)

def attachment_create(request, wikiname, pagename, attachmentname = '', **kwargs):
    wiki = Wiki.objects.get(fullname_url_cache__exact = wikiname)
    page = Page.objects.get(wiki = wiki, name__exact = pagename)
    return create_object(request, model= Attachment,
                         extra_context = { 'wiki': wiki, 'page': page, },
                         form_initial = {'page': page.uuid, 'name': attachmentname},
                         template_name = "wiki/attachment_edit.html",
                         post_save_redirect = page.get_absolute_url(),
                         **kwargs)

attachment_edit = UpdateObjectView(model = Attachment, template_name = "wiki/attachment_edit.html")

urlpatterns = patterns(
    '',

    url(r'^$',
        wiki_list,
        name="wiki-list"),

    url(r'^__add/$',
        wiki_create,
        name="wiki-create"),

    url(r'^__search$',
        v_search,
        name="wiki-search"),

    url(r'^(?P<wikiname>[a-zA-Z0-9_\-\|]+)$',
        wiki_page_list,
        name="wiki-page-list"),

    url(r'^(?P<wikiname>[a-zA-Z0-9_\-\|]+)/__edit$',
        wiki_edit,
        name="wiki-edit"),

    url(r'^(?P<wikiname>[a-zA-Z0-9_\-\|]+)/__add/$',
        v_wikipage_edit,
        dict(create=True, template_name="wiki/page_edit.html"),
        name="wiki-page-create"),

    url(r'^(?P<wikiname>[a-zA-Z0-9_\-\|]+)/(?P<pagename>[a-zA-Z0-9_\-\|\:\#]+)/new$',
        v_wikipage_edit,
        dict(create=True, template_name="wiki/page_edit.html"),
        name="wiki-page-create-named"),

    url(r'^(?P<wikiname>[a-zA-Z0-9_\-\|]+)/(?P<pagename>[a-zA-Z0-9_\-\|\:\#]+)/edit$',
        v_wikipage_edit,
        dict(create=False, template_name="wiki/page_edit.html"),
        name="wiki-page-edit"),

    url(r'^(?P<wikiname>[a-zA-Z0-9_\-\|]+)/(?P<pagename>[a-zA-Z0-9_\-\|\:\#]+)/history$',
        wikipage_history,
        name="wiki-page-history"),

    url(r'^(?P<wikiname>[a-zA-Z0-9_\-\|]+)/(?P<pagename>[a-zA-Z0-9_\-\|\:\#]+)/attachment/__add$',
        attachment_create,
        name="wiki-attachment-create"),

    url(r'^(?P<wikiname>[a-zA-Z0-9_\-\|]+)/(?P<pagename>[a-zA-Z0-9_\-\|\:\#]+)/attachment/(?P<attachmentname>[a-zA-Z0-9_\-\:\,\.\+]+)/new$',
        attachment_create,
        name="wiki-attachment-create-named"),

    url(r'^(?P<wikiname>[a-zA-Z0-9_\-\|]+)/(?P<pagename>[a-zA-Z0-9_\-\|\:\#]+)/attachment/(?P<object_id>\w+)/edit$',
        attachment_edit,
        dict(create=False, template_name="wiki/attachment_edit.html"),
        name="wiki-attachment-edit"),

    url(r'^(?P<wikiname>[a-zA-Z0-9_\-\|]+)/(?P<pagename>[a-zA-Z0-9_\-\|\:\#]+)/$',
        v_wikipage,
        dict(template_name="wiki/page_detail.html"),
        name="wiki-page-detail"),
)
