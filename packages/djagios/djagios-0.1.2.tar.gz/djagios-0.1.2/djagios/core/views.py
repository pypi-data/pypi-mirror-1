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

from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.core import serializers
from django.contrib.auth.decorators import login_required, permission_required
from django import forms

from djagios import config
from djagios.core.models import *

def _sanitize_alias(name):
    return name.replace(' ', '_').lower()

@login_required
def home(request):
    t = loader.get_template('%s/home.html'%config.theme_name)
    c = RequestContext(request, {'config': config})
    return HttpResponse(t.render(c))

@permission_required('core.add_hosttemplate', login_url='/login')
def add_host_template(request):
    if request.method == 'POST':
        form = HostTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = HostTemplateForm()
    t = loader.get_template('%s/hosttemplateadd.html'%config.theme_name)
    c = RequestContext(request, {'config':config, 'form':form,})
    return HttpResponse(t.render(c))

@permission_required('core.add_host', login_url='/login')
def add_host(request):
    if request.method == 'POST':
        form = HostForm(request.POST)
        if form.is_valid():
            h = Host()
            h.host_name = _sanitize_alias(form.cleaned_data['name'])
            h.alias = form.cleaned_data['name']
            h.address = form.cleaned_data['address']
            h.use = form.cleaned_data['template']
            h.save()
            return HttpResponseRedirect('/')
    else:
        form = HostForm()
    t = loader.get_template('%s/hostadd.html'%config.theme_name)
    c = RequestContext(request, {'config':config, 'form':form,})
    return HttpResponse(t.render(c))

@permission_required('core.delete_host', login_url='/login')
def delete_host(request):
    if request.method == 'POST':
        form = HostDeleteForm(request.POST)
        if form.is_valid():
            h = form.cleaned_data['host']
            h.delete()
            return HttpResponseRedirect('/')
    else:
        form = HostDeleteForm()
    t = loader.get_template('%s/hostdelete.html'%config.theme_name)
    c = RequestContext(request, {'config':config, 'form':form,})
    return HttpResponse(t.render(c))

@permission_required('core.change_service', login_url='/login')
def add_host_to_service(request):
    if request.method == 'POST':
        form = HostToServiceForm(request.POST)
        if form.is_valid():
            s = form.cleaned_data['service']
            h = form.cleaned_data['host']
            s.host_name.add(h)
            s.save()
            return HttpResponseRedirect('/')
    else:
        form = HostToServiceForm()
    t = loader.get_template('%s/hostservice.html'%config.theme_name)
    c = RequestContext(request, {'config':config, 'form':form,})
    return HttpResponse(t.render(c))

@permission_required('core.change_service', login_url='/login')
def remove_host_from_service(request):
    if request.method == 'POST':
        form = HostFromServiceForm(request.POST)
        if form.is_valid():
            s = form.cleaned_data['service']
            h = form.cleaned_data['host']
            if h in s.host_name.all():
                s.host_name.remove(h)
            else:
                s.host_name_n.add(h)
            s.save()
            return HttpResponseRedirect('/')
    else:
        form = HostFromServiceForm()
    t = loader.get_template('%s/hostservice.html'%config.theme_name)
    c = RequestContext(request, {'config':config, 'form':form, 'remove':True})
    return HttpResponse(t.render(c))



##################################
##### Helper methods
##################################
def _services_for_host(host_id):
    host = Host.objects.get(id=host_id)
    slist = Service.objects.filter(host_name=host_id)
    for hg in HostGroup.objects.filter(members=host_id):
        slist = slist | Service.objects.filter(hostgroup_name=hg).exclude(hostgroup_name_n=hg)
    if host.use:
        slist = slist | _services_for_host(host.use.id)
    return slist.exclude(host_name_n=host_id)

def get_services_for_host(request, host_id):
    slist = _services_for_host(host_id)
    json_value = serializers.serialize('json', slist)
    return HttpResponse(json_value, mimetype="application/javascript")

