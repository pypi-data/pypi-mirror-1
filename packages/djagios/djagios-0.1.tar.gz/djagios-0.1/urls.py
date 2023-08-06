# Copyright (c) 2009 Jochen Maes
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from django.conf.urls.defaults import *

from djagios.core import views
from djagios import config

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^djagios/', include('djagios.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
   (r'^admin/(.*)', admin.site.root),
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': '%s/login.html'%config.theme_name}),
    (r'^logout', 'django.contrib.auth.views.logout_then_login', {'login_url': '/login'},),
    (r'^@@media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': '/home/sejo/playground/djagios/src/djagios/media/%s/'%config.theme_name}),
    (r'^hosttemplate/add', views.add_host_template),
    (r'^host/add', views.add_host),
    (r'^host/delete', views.delete_host),
    (r'^service/addhost', views.add_host_to_service),
    (r'^service/removehost', views.remove_host_from_service),
    (r'^json/servicesforhost/(?P<host_id>.*)/$',views.get_services_for_host ),
    (r'^$', views.home),
)
