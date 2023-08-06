from django.conf.urls.defaults import *
from django.conf import settings

import softwarefabrica.django.wiki.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',

    # Admin
    #(r'^admin/', include('django.contrib.admin.urls')),

    # Uncomment the next line to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line for to enable the admin:
    (r'^admin/(.*)', admin.site.root),

    # login
    #url(r'^login/$',  'django.contrib.auth.views.login', {'template_name': 'login.html'}, name="login"),
    ##url(r'^logout/$', common.views.v_logout, name="logout"),

    # permission denied
    ##url(r'^denied/$', common.views.v_perm_denied, name="perm-denied"),

    (r'', include('softwarefabrica.django.wiki.urls')),
)

if settings.DEBUG:
     urlpatterns += patterns(
         '',

         # static media (development only)
         (r'^static/(?P<path>.*)$',  'django.views.static.serve', {'document_root': settings.STATIC_ROOT}), # STATIC_MEDIA_DIR
         (r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}), # UPLOAD_MEDIA_DIR
    )
