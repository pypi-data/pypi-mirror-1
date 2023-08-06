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

from django.contrib import admin
from djagios.core.models import  *

class HostAdmin(admin.ModelAdmin):
    list_display = ('alias', 'host_name', 'name', 'address')

class HostGroupAdmin(admin.ModelAdmin):
    list_display = ('alias', 'hostgroup_name')

class NagiosCfgAdmin(admin.ModelAdmin):
    pass

class CfgPathAdmin(admin.ModelAdmin):
    pass

class CommandAdmin(admin.ModelAdmin):
    pass

class CheckCommandAdmin(admin.ModelAdmin):
    pass

class ServiceAdmin(admin.ModelAdmin):
    pass

class ServiceGroupAdmin(admin.ModelAdmin):
    pass

class ContactAdmin(admin.ModelAdmin):
    pass

class ContactGroupAdmin(admin.ModelAdmin):
    pass

class TimePeriodAdmin(admin.ModelAdmin):
    pass

class TimeRangeAdmin(admin.ModelAdmin):
    pass

class HostTemplateAdmin(admin.ModelAdmin):
    pass

admin.site.register(Host, HostAdmin)
admin.site.register(HostGroup, HostGroupAdmin)
admin.site.register(NagiosCfg, NagiosCfgAdmin)
admin.site.register(CfgPath, CfgPathAdmin)
admin.site.register(Command, CommandAdmin)
admin.site.register(CheckCommand, CheckCommandAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceGroup, ServiceGroupAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(ContactGroup, ContactGroupAdmin)
admin.site.register(TimePeriod, TimePeriodAdmin)
admin.site.register(TimeRange, TimeRangeAdmin)
admin.site.register(HostTemplate, HostTemplateAdmin)
