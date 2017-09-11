from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
import profiles.urls
import accounts.urls
from . import views

urlpatterns = [
    url(r'^$', views.HomePage.as_view(), name='home'),
    url(r'^about/$', views.AboutPage.as_view(), name='about'),
    url(r'^users/', include(profiles.urls, namespace='profiles')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(accounts.urls, namespace='accounts')),

    url(r'^browse$', views.browse, name="browse"),
    url(r'^s3files$', views.get_s3_files, name="get_s3_files"),
    url(r'^localfiles$', views.get_local_files, name="get_local_files"),
    url(r'^runtask/pack$', views.runtask_pack, name="runtask_pack"),
    url(r'^runtask/upload$', views.runtask_upload, name="runtask_upload"),
    url(r'^runtask/delete$', views.runtask_delete, name="runtask_delete"),
    url(r'^taskstatus$', views.get_task_status, name="get_task_status"),
]

# User-uploaded files like profile pics need to be served in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Include django debug toolbar if DEBUG is on
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
