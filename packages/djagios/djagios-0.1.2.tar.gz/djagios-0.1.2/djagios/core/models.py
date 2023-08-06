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


"""The models module defines the nagios configuration datastructures as classes.

For obvious reasons you should also check the Nagios documentation for the attributes.
Each attribute has been named as the configuration option in nagios.
example::

    define command {
        command_name               com1
        command_line               line1
    }

The previous example is a basic definition of the command object in nagios. 
We mapped this to the following api::

    >>> com = Command()
    >>> com.command_name = 'com1'
    >>> com.command_line = 'line1'

Where we could we would link to another object.
example::

    define contactgroup {
        contactgroup_name           cg1
        alias                       Contact group 1
        members                     admins,nagios
    }

To map this example we can link the members section to a list of Contact objects.
This would be done with a many to many relationship. This resulted in following api::

    >>> cg = ContactGroup()
    >>> cg.contactgroup_name = 'cg1'
    >>> cg.alias = 'Contact group 1'
    >>> cg.save()
    >>> cg.members.add(Contact.get('admins'))
    >>> cg.members.add(Contact.get('nagios'))

As you can see we saved before adding a member. This is to be able to save the 
many to many references correctly. So as long as the object has no ID we cannot 
add many to many relations.
"""
import os
import logging
import StringIO

from django.db import models
from django.core import serializers
from django import forms

from djagios.core.exceptions import ParseError

HOST_STATES = (
        ('d', 'down'),
        ('u', 'unreachable'),
        ('o', 'up')
        )

LOG_ROTATION_METHODS = (
        ('n', 'none'),
        ('h', 'hourly'),
        ('d', 'daily'),
        ('w', 'weekly'),
        ('m', 'monthly'),
        )

OPEN_FILE_MODES = (
        ('a', 'append'),
        ('w', 'write'),
        ('p', 'non-blocking read-write'),
        )

class NagiosObject:
    """Abstract class for all NagiosObjects

    Each NagiosObject contains following methods:
     - :func:`get`
     - :func:`parse_to_nagios_cfg`

    Basicly :func:`get` will fetch the information from the database,
    :func:`export` will export the object to a nagios configuration string
    """

    @classmethod
    def get(self, criterion):
        """Classmethod :func:`get` should always provide a way to fetch an object from the
        database by providing on of the key values.
        Returns the object or raises an error if no object with that criterion
        has been found

        :param criterion: Criterion to fetch the object
        :type criterion: :class:`str`
        :rtype: :class:`NagiosObject`
        :raises: :exc:`DoesNotExist`
        """
        raise NotImplementedError('Method not implemented go slap the developer!')

    def serialize(self, type='python'):
        """:func:`serialize` Allows you to serialize the object to the possible 
        serializers in django. Right now we can serialize to following formats:

          - json
          - python 
          - xml
          - yaml

       For more information on the serializers in django please visit:
       http://docs.djangoproject.com/en/dev/topics/serialization/

        :param type: Type of the serialization default set to python
        :type type: :class:`str`
        :return str: String containing the the serialized information
        """
        serializer = serializers.get_serializer(type)()
        return serializer.serialize((self,))

    def parse_to_nagios_cfg(self, path=None):
        """Each NagiosObject should provide a way to parse the object to a string containing
        the nagios configuration block.

        :param path: Optional, allows to pass the dir where the file will be written.
        :type path: :class:`str`
        :rtype: :class:`str`
        """
        raise NotImplementedError('Method not implemented go slap the developer!')

class Host (NagiosObject, models.Model):
    """Host is the class that defines the nagios host model.
    It uses foreign keys and many2many relationships to have a
    basic validation and control. 
    At this time Django does not support validation for attributes
    so this will be included later.

    Before you can start assigning m2m relations you need to save the
    object first. Make sure you add a host_name or name before saving.
    This to allow you to fetch the host easily::

        >>> from djagios.core.models import Host
        >>> host = Host()
        >>> host.host_name="host01"
        >>> host.save()

    :class:`Host` has following m2m relations:
     - parents: :class:`Host`
     - hostgroups: :class:`HostGroup`
     - contacts: :class:`Contact`
     - contact_groups: :class:`ContactGroup`

    :class:`Host` has following Foreign Keys:
     - use: :class:`Host`
     - check_command: :class:`CheckCommand`
     - check_period: :class:`TimePeriod`
     - event_handler: :class:`CheckCommand`
     - notification_period: :class:`TimePeriod`

     :parent: :class:`NagiosObject`
    """
    FILE_NAME = 'host.cfg'
    use = models.ForeignKey('self', related_name='H_use_H', \
            blank=True,null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    host_name = models.CharField(max_length=255, blank=True,null=True)
    alias = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    parents = models.ManyToManyField('self', related_name='H_parents_H',\
            blank=True, null=True)
    hostgroups = models.ManyToManyField('HostGroup', related_name='H_hg_HG',\
            blank=True,null=True)
    check_command = models.ForeignKey('CheckCommand', related_name='H_cc_CC,', blank=True,null=True)
    check_period = models.ForeignKey('TimePeriod', related_name='H_cp_TP', blank=True,null=True)
    initial_state = models.CharField(max_length=1, choices=HOST_STATES, blank=True, null=True)
    max_check_attempts = models.IntegerField(blank=True, null=True)
    check_interval = models.IntegerField(blank=True, null=True)
    retry_interval = models.IntegerField(blank=True, null=True)
    active_checks_enabled = models.NullBooleanField(blank=True, null=True)
    passive_checks_enables = models.NullBooleanField(blank=True, null=True)
    obsess_over_host = models.NullBooleanField(blank=True, null=True)
    check_freshness = models.NullBooleanField(blank=True, null=True)
    freshness_threshold = models.IntegerField(blank=True, null=True)
    event_handler = models.ForeignKey('CheckCommand', related_name='H_eh_CC',\
            blank=True, null=True)
    event_handler_enabled = models.NullBooleanField(blank=True, null=True)
    low_flap_threshold = models.IntegerField(blank=True, null=True)
    high_flap_threshold = models.IntegerField(blank=True, null=True)
    flap_detection_enabled = models.NullBooleanField(blank=True, null=True)
    flap_detection_options = models.CharField(max_length=10, blank=True,null=True)
    process_perf_data = models.NullBooleanField(blank=True, null=True)
    retain_status_information = models.NullBooleanField(blank=True, null=True)
    retain_nonstatus_information = models.NullBooleanField(blank=True, null=True)
    contacts = models.ManyToManyField('Contact', related_name='H_c_C',\
            blank=True,null=True)
    contact_groups = models.ManyToManyField('ContactGroup', related_name='H_cg_CG',\
            blank=True, null=True)
    notification_interval = models.IntegerField(blank=True, null=True)
    first_notification_delay = models.IntegerField(blank=True, null=True)
    notification_period = models.ForeignKey('TimePeriod', related_name='H_np_TP',\
            blank=True, null=True)
    notification_options = models.CharField(max_length=20, blank=True, null=True)
    notifications_enabled = models.NullBooleanField(blank=True, null=True)
    stalking_options = models.CharField(max_length=10,blank=True, null=True)
    notes = models.TextField(blank=True,null=True)
    notes_url = models.URLField(verify_exists=True, blank=True, null=True)
    action_url = models.URLField(verify_exists=True, blank=True, null=True)
    icon_image = models.CharField(max_length=100, blank=True, null=True)
    icon_image_alt = models.CharField(max_length=255, blank=True, null=True)
    vrml_image = models.CharField(max_length=255, blank=True, null=True)
    statusmap_image = models.CharField(max_length=255, blank=True, null=True)
    x_coord = models.IntegerField(blank=True, null=True)
    y_coord = models.IntegerField(blank=True, null=True)
    z_coord = models.IntegerField(blank=True, null=True)
    register = models.NullBooleanField(blank=True,null=True)

    def Meta(self):
        """Here for Host we define the unique key that exists out of 2 attributes
        host_name and name.
        """
        unique_together = (('host_name', 'name', 'address'),)

    @classmethod
    def get(self, criterion):
        """classmethod that will allow you to fetch a :class:`Host` object
        from the database.

        :param criterion: criterion you wish to supply, for :class:`Host` this is host_name or name
        :type criterion: str
        :rtype: :class:`Host` or None
        :raises: :exc:`DoesNotExist`

        """
        o = None
        try:
            o = Host.objects.get(name=criterion)
            return o
        except Host.DoesNotExist:
            try:
                o = Host.objects.get(host_name=criterion)
                return o
            except Host.DoesNotExist:
                raise Host.DoesNotExist('Cannot find the host based on your criterion: %s'%criterion)

    def parse_to_nagios_cfg(self, path=None):
        """:func:`parse_to_nagios_cfg` will create a nagios formatted block of the
        current :class:`Host` object.

        :param path: Optional, allows to pass the dir where the file will be written.
        :type path: :class:`str`
        :rtype: :class:`str`
        :raises: :Exc:`djagios.core.exceptions.ParseError`

        """
        s = StringIO.StringIO()
        s.write('define host {\n')
        for attr in self._meta.get_all_field_names():
            if not hasattr(self, attr) or attr == 'id':
                continue
            if attr in ('parents', 'hostgroups', 'contacts', 'contact_groups', ):
                if len(getattr(self,attr).values()) > 0:
                    vals = list()
                    for i in getattr(self,attr).iterator():
                        vals.append(str(i))
                    s.write('\t%s\t\t%s\n'%(attr, ",".join(vals)))
                    continue
            value = getattr(self, attr)
            if not value and not attr == 'register':
                continue
            if isinstance(value, (str,int, unicode, long,\
                    CheckCommand, Service, Host, HostGroup, TimePeriod)):
                s.write('\t%s\t\t%s\n'%(attr,value))
        s.write('}\n')
        s.flush()
        ret = s.getvalue()
        s.close()
        return ret

    def __str__(self):
        return self.host_name or self.name

class HostGroup(NagiosObject, models.Model):
    """Definition for the Nagios hostgroup object.

    :class:`HostGroup` has following m2m fields:
     - members: :class:`Host`
     - hostgroup_members: :class:`HostGroup`
    """
    FILE_NAME = 'hostgroup.cfg'
    hostgroup_name = models.CharField(max_length=255, unique=True)
    alias = models.CharField(max_length=255, blank=True,null=True)
    members = models.ManyToManyField(Host, related_name='HG_m_H',\
            blank=True,null=True)
    hostgroup_members= models.ManyToManyField('self', related_name='HG_hgm_HG',\
            blank=True,null=True)
    notes = models.TextField(blank=True,null=True)
    notes_url = models.URLField(verify_exists=True, blank=True,null=True)
    action_url = models.URLField(verify_exists=True, blank=True,null=True)

    @classmethod
    def get(self, criterion):
        """classmethod that will allow you to fetch a :class:`HostGroup` object
        from the database.

        :param criterion: criterion you wish to supply, for :class:`HostGroup` this is the hostgroup_name
        :type criterion: str
        :rtype: :class:`HostGroup` or None
        :raises: :exc:`DoesNotExist`

        """
        o = None
        try:
            o = HostGroup.objects.get(hostgroup_name=criterion)
            return o
        except HostGroup.DoesNotExist:
            raise HostGroup.DoesNotExist('Cannot find the hostgroup based on your criterion: %s'%criterion)

    def parse_to_nagios_cfg(self, path=None):
        """:func:`parse_to_nagios_cfg` will create a nagios formatted block of the
        current :class:`HostGroup` object.

        :param path: Optional, allows to pass the dir where the file will be written.
        :type path: :class:`str`
        :rtype: :class:`str`
        :raises: :Exc:`djagios.core.exceptions.ParseError`

        """
        s = StringIO.StringIO()
        s.write('define hostgroup {\n')
        for attr in self._meta.get_all_field_names():
            if not hasattr(self, attr) or attr == 'id':
                continue
            if attr in ('members', 'hostgroup_members',):
                if len(getattr(self,attr).values()) > 0:
                    vals = list()
                    for i in getattr(self,attr).iterator():
                        vals.append(str(i))
                    s.write('\t%s\t\t%s\n'%(attr, ",".join(vals)))
                    continue
            value = getattr(self, attr)
            if not value:
                continue
            if isinstance(value, (str,int, unicode, long)):
                s.write('\t%s\t\t%s\n'%(attr,value))
                continue
            if isinstance(value, bool):
                if value:
                    s.write('\t%s\t\t%s\n'%(attr,'1'))
                else:
                    s.write('\t%s\t\t%s\n'%(attr,'0'))

        s.write('}\n')
        s.flush()
        ret = s.getvalue()
        s.close()
        return ret

    def __str__(self):
        return self.hostgroup_name

class Service(NagiosObject, models.Model):
    """Service is the class that defines the Nagios service object. 

    :class:`Service` has following m2m fields:
     - host_name: :class:`Host`
     - hostgroup_name: :class:`HostGroup`
     - host_name_n: :class:`Host`
     - hostgroup_name_n: :class:`HostGroup`
     - servicegroups: :class:`ServiceGroup`
     - contacts: :class:`Contact`
     - contact_groups: :class:`ContactGroup`

    :class:`Service` has following Foreign keys:
     - use: :class:`Service`
     - check_command: :class:`CheckCommand`
     - check_period: :class:`TimePeriod`
     - event_handler: :class:`CheckCommand`
     - notification_period: :class:`TimePeriod`
    """
    FILE_NAME = 'service.cfg'
    use = models.ForeignKey('Service', related_name='S_use_S', \
            blank=True,null=True)
    name = models.CharField(max_length=100, blank=True)
    host_name = models.ManyToManyField(Host, related_name='S_hostname_H',\
            blank=True,null=True)
    hostgroup_name = models.ManyToManyField(HostGroup, related_name='S_hostgroup_HG',\
            blank=True,null=True)
    host_name_n = models.ManyToManyField(Host, related_name='S_hostname_n_H',\
            blank=True,null=True)
    hostgroup_name_n = models.ManyToManyField(HostGroup, related_name='S_hostgroup_n_HG',\
            blank=True,null=True)
    service_description = models.CharField(max_length=255, blank=True,null=True)
    display_name = models.CharField(max_length=255, blank=True)
    servicegroups = models.ManyToManyField('ServiceGroup', related_name='S_sg_SG',\
            blank=True,null=True)
    is_volatile = models.NullBooleanField(blank=True,null=True)
    check_command = models.ForeignKey('CheckCommand', related_name='S_cc_CC',\
            blank=True,null=True)
    initial_state = models.CharField(max_length=1,blank=True, null=True)
    max_check_attempts = models.IntegerField(blank=True,null=True)
    check_interval = models.IntegerField(blank=True,null=True)
    retry_interval = models.IntegerField(blank=True,null=True)
    active_checks_enabled = models.NullBooleanField(blank=True,null=True)
    passive_checks_enabled = models.NullBooleanField(blank=True,null=True)
    check_period = models.ForeignKey('TimePeriod',related_name='S_cp_TP',\
            blank=True,null=True)
    obsess_over_service = models.NullBooleanField(default=False)
    check_freshness = models.NullBooleanField(blank=True,null=True)
    freshness_threshold = models.IntegerField(blank=True,null=True)
    event_handler = models.ForeignKey('CheckCommand', related_name='S_eh_CC',\
            blank=True, null=True)
    event_handler_enabled = models.NullBooleanField(default=False)
    low_flap_threshold = models.IntegerField(default=0)
    high_flap_threshold = models.IntegerField(default=0)
    flap_detection_enabled = models.NullBooleanField(default=False)
    flap_detection_options = models.CharField(max_length=10, blank=True)
    process_perf_data = models.NullBooleanField(default=False)
    retain_status_information = models.NullBooleanField()
    retain_nonstatus_information = models.NullBooleanField(default=False)
    contacts = models.ManyToManyField('Contact', related_name='S_c_C',\
            blank=True,null=True)
    contact_groups = models.ManyToManyField('ContactGroup', related_name='S_cg_CG',\
            blank=True,null=True)
    notification_interval = models.IntegerField(blank=True,null=True)
    first_notification_delay = models.IntegerField(blank=True,null=True)
    notification_period = models.ForeignKey('TimePeriod', related_name='S_np_TP',\
            blank=True,null=True)
    notification_options = models.CharField(max_length=10, blank=True)
    notifications_enabled = models.NullBooleanField()
    stalking_options = models.CharField(max_length=10,blank=True)
    notes = models.TextField(blank=True)
    notes_url = models.URLField(verify_exists=True,blank=True)
    action_url = models.URLField(verify_exists=True,blank=True)
    icon_image = models.CharField(max_length=100,blank=True)
    icon_image_alt = models.CharField(max_length=255,blank=True)
    register = models.NullBooleanField(blank=True, null=True)

    def __str__(self):
        return self.service_description or self.name

    def Meta(self):
        unique_together = (('name', 'host_name', 'service_description',),)

    @classmethod
    def get(self,criterion):
        """classmethod that will allow you to fetch a :class:Service` object
        from the database.

        :param criterion: criterion you wish to supply, for :class:`Service` this is the service_description or name
        :type criterion: str
        :rtype: :class:`Service` or None
        :raises: :exc:`DoesNotExist`
        """
        o = None
        try:
            o = Service.objects.get(service_description=criterion)
            return o
        except Service.DoesNotExist:
            try:
                o = Service.objects.get(name=criterion)
                return o
            except Service.DoesNotExist:
                raise Service.DoesNotExist('Cannot find the service based on your criterion: %s'%criterion)

    def parse_to_nagios_cfg(self, path=None):
        """:func:`parse_to_nagios_cfg` will create a nagios formatted block of the
        current :class:`Service` object.

        :rtype: :class:`str`
        :raises: :Exc:`djagios.core.exceptions.ParseError`

        """
        s = StringIO.StringIO()
        s.write('define service {\n')
        for attr in self._meta.get_all_field_names():
            if not hasattr(self, attr) or attr == 'id' or attr == 'id':
                continue
            if attr in ('host_name', 'host_name_n', 'hostgroup_name', 'servicegroups'\
                    'hostgroup_name_n', 'contacts', 'contact_groups', ):
                if len(getattr(self,attr).values()) > 0:
                    vals = list()
                    for i in getattr(self,attr).iterator():
                        vals.append(str(i))
                    s.write('\t%s\t\t%s\n'%(attr, ",".join(vals)))
                    continue
            value = getattr(self, attr)
            if not value:
                continue
            if isinstance(value, (str,int, unicode, bool, long,\
                    CheckCommand, Service, TimePeriod)):
                s.write('\t%s\t\t%s\n'%(attr,value))
        s.write('}\n')
        s.flush()
        ret = s.getvalue()
        s.close()
        return ret

class ServiceGroup(NagiosObject, models.Model):
    """Definition for the Nagios servicegroup object.

    :class:`ServiceGroup` has following m2m fields:
     - members: :class:`Service`
     - servicegroup_members: :class:`ServiceGroup`
    """
    FILE_NAME='servicegroup.cfg'
    servicegroup_name = models.CharField(max_length=255, unique=True)
    alias = models.CharField(max_length=255,blank=True)
    members = models.ManyToManyField(Service, related_name='SG_members_S',\
            blank=True,null=True)
    servicegroup_members= models.ManyToManyField('self', related_name='SG_sgm_SG',\
            blank=True,null=True)
    notes = models.TextField()
    notes_url = models.URLField(verify_exists=True)
    action_url = models.URLField(verify_exists=True)

    @classmethod
    def get(self, criterion):
        """classmethod that will allow you to fetch a :class:ServiceGroup` object
        from the database.

        :param criterion: criterion you wish to supply, for :class:`ServiceGroup` this is the servicegroup_name
        :type criterion: str
        :rtype: :class:`ServiceGroup` or None
        :raises: :exc:`DoesNotExist`
        """
        o = None
        try:
            o = ServiceGroup.objects.get(servicegroup_name=criterion)
            return o
        except ServiceGroup.DoesNotExist:
            raise Contact.DoesNotExist('Cannot find the servicegroup based on your criterion: %s'%criterion)

    def parse_to_nagios_cfg(self, path=None):
        """:func:`parse_to_nagios_cfg` will create a nagios formatted block of the
        current :class:`ServiceGroup` object.

        :rtype: :class:`str`
        :raises: :Exc:`djagios.core.exceptions.ParseError`

        """
        s = StringIO.StringIO()
        s.write('define servicegroup {\n')
        for attr in self._meta.get_all_field_names():
            if not hasattr(self, attr) or attr == 'id':
                continue
            if attr in ('members', 'servicegroup_members',):
                if len(getattr(self,attr).values()) > 0:
                    vals = list()
                    for i in getattr(self,attr).iterator():
                        vals.append(str(i))
                    s.write('\t%s\t\t%s\n'%(attr, ",".join(vals)))
                    continue
            value = getattr(self, attr)
            if not value:
                continue
            if isinstance(value, (str,int, unicode, bool, long,\
                    CheckCommand, Service)):
                s.write('\t%s\t\t%s\n'%(attr,value))
        s.write('}\n')
        s.flush()
        ret = s.getvalue()
        s.close()
        return ret

    def __str__(self):
        return self.servicegroup_name

class Contact(NagiosObject, models.Model):
    """Definition for the Nagios contact object

    :class:`Contact` has following :class:`django.db.models.ManyToManyField` attributes:
     - :attr:`contactgroups`
     - :attr:`host_notification_commands`
     - :attr:`service_notification_options`

    :class:`Contact` has following :class:`django.db.models.ForeignKey` attributes:
     - :attr:`use`
     - :attr:`host_notification_period`
     - :attr:`service_notification_period`

    """
    FILE_NAME = 'contact.cfg'
    use = models.ForeignKey('Contact', related_name='C_use_C', \
            blank=True,null=True)
    name = models.CharField(max_length=100, blank=True)
    contact_name = models.CharField(max_length=255, blank=True)
    alias = models.CharField(max_length=255, blank=True)
    contactgroups = models.ManyToManyField('ContactGroup', related_name='C_cg_CG',\
            blank=True, null=True)
    host_notifications_enabled = models.NullBooleanField(blank=True,null=True)
    service_notifications_enabled = models.NullBooleanField(blank=True,null=True)
    host_notification_period = models.ForeignKey('TimePeriod', related_name='C_hnp_TP',\
            blank=True, null=True)
    service_notification_period = models.ForeignKey('TimePeriod', related_name='C_snp_TP',\
            blank=True, null=True)
    host_notification_options = models.CharField(max_length=20)
    service_notification_options = models.CharField(max_length=20)
    host_notification_commands = models.ManyToManyField('CheckCommand',related_name='C_hnc_CC',\
            blank=True, null=True)
    service_notification_commands = models.ManyToManyField('CheckCommand', related_name='C_snc_CC',\
            blank=True, null=True)
    email = models.EmailField(blank=True)
    pager = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    can_submit_commands = models.NullBooleanField(blank=True,null=True)
    retain_status_information = models.NullBooleanField(blank=True,null=True)
    retain_nonstatus_information = models.NullBooleanField(blank=True,null=True)
    register = models.NullBooleanField(blank=True,null=True)

    @classmethod
    def get(self, criterion):
        """classmethod that will allow you to fetch a :class:Contact` object
        from the database.

        :param criterion: criterion you wish to supply, for :class:`Contact` this is the :attr:`name` or :attr:`contact_name`
        :type criterion: str
        :rtype: :class:`Contact` or :class:`None`
        :raises: :exc:`DoesNotExist`

        """
        o = None
        try:
            o = Contact.objects.get(name=criterion)
            return o
        except Contact.DoesNotExist:
            try:
                o = Contact.objects.get(contact_name=criterion)
                return o
            except Contact.DoesNotExist:
                raise Contact.DoesNotExist('Cannot find the contact based on your criterion: %s'%criterion)

    def parse_to_nagios_cfg(self, path=None):
        """:func:`parse_to_nagios_cfg` will create a nagios formatted block of the
        current :class:`Contact` object.

        :param path: Optional, allows to pass the dir where the file will be written.
        :type path: :class:`str`
        :rtype: :class:`str`
        :raises: :Exc:`djagios.core.exceptions.ParseError`

        """
        s = StringIO.StringIO()
        s.write('define contact {\n')
        for attr in self._meta.get_all_field_names():
            if not hasattr(self, attr) or attr == 'id':
                continue
            if attr in ('contactgroups', 'host_notification_commands',\
                    'service_notification_commands',):
                if len(getattr(self,attr).values()) > 0:
                    vals = list()
                    for i in getattr(self,attr).iterator():
                        vals.append(str(i))
                    s.write('\t%s\t\t%s\n'%(attr, ",".join(vals)))
                    continue
            value = getattr(self, attr)
            if not value:
                continue
            if isinstance(value, (str,int, unicode, bool, long,\
                    CheckCommand, Service, TimePeriod)):
                s.write('\t%s\t\t%s\n'%(attr,value))
        s.write('}\n')
        s.flush()
        ret = s.getvalue()
        s.close()
        return ret

    def Meta(self):
        unique_together = (('name', 'contact_name',),)

    def __str__(self):
        return self.contact_name or self.name

class ContactGroup(NagiosObject, models.Model):
    """Definition for the Nagios contactgroup object

    :class:`ContactGroup` has following :class:`django.db.models.ManyToManyField` attributes:
     - :attr:`members`
     - :attr:`contactgroup_members`

    """
    FILE_NAME = 'contactgroup.cfg'
    contactgroup_name = models.CharField(max_length=255, unique=True)
    alias = models.CharField(max_length=255)
    members = models.ManyToManyField(Contact, related_name='CG_m_C',\
            blank=True,null=True)
    contactgroup_members= models.ManyToManyField('self', related_name='CG_cgm_CG',\
            blank=True,null=True)

    @classmethod
    def get(self,criterion):
        """classmethod that will allow you to fetch a :class:ContactGroup` object
        from the database.

        :param criterion: criterion you wish to supply, for :class:`ContactGroup` this is the :attr:`contactgroup_name`
        :type criterion: str
        :rtype: :class:`ContactGroup` or :class:`None`
        :raises: :exc:`DoesNotExist`

        """
        o = None
        try:
            o = ContactGroup.objects.get(contactgroup_name=criterion)
            return o
        except ContactGroup.DoesNotExist:
            raise ContactGroup.DoesNotExist('Cannot find the contact group based on your criterion: %s'%criterion)

    def parse_to_nagios_cfg(self, path=None):
        """:func:`parse_to_nagios_cfg` will create a nagios formatted block of the
        current :class:`ContactGroup` object.

        :param path: Optional, allows to pass the dir where the file will be written.
        :type path: :class:`str`
        :rtype: :class:`str`
        :raises: :Exc:`djagios.core.exceptions.ParseError`

        """
        s = StringIO.StringIO()
        s.write('define contactgroup {\n')
        for attr in self._meta.get_all_field_names():
            if not hasattr(self, attr) or attr == 'id':
                continue
            if attr in ('contactgroups', 'host_notification_commands',\
                    'service_notification_commands',):
                if len(getattr(self,attr).values()) > 0:
                    vals = list()
                    for i in getattr(self,attr).iterator():
                        vals.append(str(i))
                    s.write('\t%s\t\t%s\n'%(attr, ",".join(vals)))
                    continue
            value = getattr(self, attr)
            if not value:
                continue
            if isinstance(value, (str,int, unicode, bool, long,\
                    CheckCommand, Service, TimePeriod)):
                s.write('\t%s\t\t%s\n'%(attr,value))
        s.write('}\n')
        s.flush()
        ret = s.getvalue()
        s.close()
        return ret

    def __str__(self):
        return self.contactgroup_name

class Command(NagiosObject, models.Model):
    """Definition for the Nagios command object"""
    FILE_NAME = 'command.cfg'
    command_name = models.CharField(max_length=255,unique=True)
    command_line = models.TextField()

    @classmethod
    def get(self,criterion):
        """classmethod that will allow you to fetch a :class:Command` object
        from the database.

        :param criterion: criterion you wish to supply, for :class:`Command` this is the :attr:`command_name`
        :type criterion: str
        :rtype: :class:`Command` or :class:`None`
        :raises: :exc:`DoesNotExist`


        As the command_name is usually given with the parameters attached to it, we split on ! and take the first entry
        of the resulting list. So there is no need to parse the check_command entry before passing to this function.

        """
        o = None
        try:
            o = Command.objects.get(command_name=criterion.split('!')[0])
            return o
        except Command.DoesNotExist:
            raise Command.DoesNotExist('Cannot find the command based on you criterion %s'%criterion)

    def parse_to_nagios_cfg(self, path=None):
        """:func:`parse_to_nagios_cfg` will create a nagios formatted block of the
        current :class:`Command` object.

        :param path: Optional, allows to pass the dir where the file will be written.
        :type path: :class:`str`
        :rtype: :class:`str`
        :raises: :Exc:`djagios.core.exceptions.ParseError`

        """
        s = StringIO.StringIO()
        s.write('define command {\n')
        for attr in self._meta.get_all_field_names():
            if not hasattr(self, attr) or attr == 'id':
                continue
            value = getattr(self, attr)
            if not value:
                continue
            if isinstance(value, (str,int, unicode, bool,)):
                s.write('\t%s\t\t%s\n'%(attr,value))
        s.write('}\n')
        s.flush()
        ret = s.getvalue()
        s.close()
        return ret

    def __str__(self):
        return self.command_name

class CheckCommand(models.Model):
    """:class:`CheckCommand` is the class that is used in :class:`Host`, :class:`Service`.
    This contains a foreign key to the :class:`Command` object and has an extra field with it's
    parameters. We keep them in the format like Nagios uses them, then we do not need another
    database tablerow for each possible parameter.
    """
    command = models.ForeignKey('Command')
    paramline = models.CharField(max_length=255)

    class Meta:
        unique_together = ('command', 'paramline',)

    @classmethod
    def get(self, criterion):
        """A classmethod that will return a :class:`CheckCommand` object.
        If we do not find a corresponding object in the database, we will
        save one ourselved and return that one.

        :param criterion: Criterion for the object you want to fetch
        :type criterion: :class:`str`
        :rtype: :class:`CheckCommand`
        """
        c_name = criterion.split('!')[0]
        c_attr = criterion.replace(c_name, '')
        try:
            o = CheckCommand.objects.get(command=Command.get(c_name), paramline=c_attr)
            return o
        except CheckCommand.DoesNotExist:
            o = CheckCommand(command=Command.get(c_name), paramline=c_attr)
            o.save()
            return o

    def __str__(self):
        return "%s%s"%(self.command, self.paramline)

    def __repr__(self):
        return self.__str__()

class TimePeriod(NagiosObject, models.Model):
    """Definition for the Nagios TimePeriod object

    Ths TimePeriod object is a special object. Nagios allows to configure ranges.
    As the key of a range is chosen by the admin we cannot foresee columns with their names.
    Thus we parse the ranges into :class:`TimeRange` objects and link them to this object.

    There are also multiple excludes possible, each exclude is a reference to a :class:`TimePeriod`.

    :class:`TimePeriod` has following :class:`django.db.models.ManyToManyField` attributes:
     - :attr:`ranges`
     - :attr:`exclude`
    """
    FILE_NAME = 'timeperiod.cfg'
    timeperiod_name = models.CharField(max_length=255, unique=True)
    alias = models.CharField(max_length=255)
    ranges = models.ManyToManyField('TimeRange', related_name='TP_r_TR')
    exclude = models.ManyToManyField('self', related_name='TP_e_TP',\
            blank=True,null=True)

    def __str__(self):
        return self.timeperiod_name

    def parse_to_nagios_cfg(self, path=None):
        """:func:`parse_to_nagios_cfg` will create a nagios formatted block of the
        current :class:`TimePeriod` object.

        :param path: Optional, allows to pass the dir where the file will be written.
        :type path: :class:`str`
        :rtype: :class:`str`
        :raises: :Exc:`djagios.core.exceptions.ParseError`

        """
        s = StringIO.StringIO()
        s.write('define timeperiod {\n')
        for attr in self._meta.get_all_field_names():
            if not hasattr(self, attr) or attr == 'id':
                continue
            if attr in ('ranges', 'exclude',):
                if len(getattr(self,attr).values()) > 0:
                    for i in getattr(self,attr).iterator():
                        s.write('\t%s\t\t%s\n'%(str(i),i.value ))
                    continue
            value = getattr(self, attr)
            if not value:
                continue
            if isinstance(value, (str,int,unicode,bool)):
                s.write('\t%s\t\t%s\n'%(attr,value))
        s.write('}\n')
        s.flush()
        ret = s.getvalue()
        s.close()
        return ret

    @classmethod
    def get(self, criterion):
        """classmethod that will allow you to fetch a :class:TimePeriod` object
        from the database.

        :param criterion: criterion you wish to supply, for :class:`TimePeriod` this is the :attr:`timeperiod_name`
        :type criterion: str
        :rtype: :class:`TimePeriod` or :class:`None`
        :raises: :exc:`DoesNotExist`

        """
        o = None
        try:
            o = TimePeriod.objects.get(timeperiod_name=criterion)
            return o
        except TimePeriod.DoesNotExist:
            raise TimePeriod.DoesNotExist('Cannot find the TimePeriod based on your criterion %s'%criterion)

class TimeRange(models.Model):
    """A helper class for the :class:`TimePeriod` object

    By creating a key-value pair object we can simply add the :class:`TimeRange` to the
    :class:`TimePeriod` for the [weekdays] and [exceptions] directives.
    Nagios allows those directives to have a unique key. This was the only way to solve it
    from a database viewpoint.
    """
    key = models.CharField(max_length=255, unique=True)
    value = models.CharField(max_length=255)

    @classmethod
    def get(self,k, v):
        """:func:`get` will check the database if an object exists with the
        provided key and return it. It it does not exist, :func:`get` will create
        a :class:`TimeRange` and save it to the database.

        :param k: key for the :class:`TimeRange`
        :type k: str
        :param v: value for the :class:`TimeRange`
        :type v: str
        :return: :class:`TimeRange`
        """
        try:
            o = TimeRange.objects.get(key=k)
            return o
        except TimeRange.DoesNotExist:
            o = TimeRange()
            o.key = k.strip()
            o.value = v.strip()
            o.save()
            return o

    def __str__(self):
        return self.key

class ServiceDependency(NagiosObject, models.Model):
    """Definition for the Nagios servicedependency object.

    :class:`ServiceDependency` has following :class:`django.db.models.ManyToManyField` attributes:
     - :attr:`dependent_host_name`
     - :attr:`dependent_hostgroup_name`
     - :attr:`host_name`
     - :attr:`hostgroup_name`

    :class:`ServiceDependency` has following :class:`django.db.models.ForeignKey` attributes:
     - :attr:`dependent_service_description`
     - :attr:`service_description`
     - :attr:`dependency_period`

    """
    dependent_host_name = models.ManyToManyField('Host', related_name='SD_dh_H',\
            blank=True, null=True)
    dependent_hostgroup_name = models.ManyToManyField('HostGroup', related_name='SD_dhg_HG',\
            blank=True, null=True)
    dependent_service_description = models.ForeignKey('Service', related_name='SD_ds_S')
    host_name = models.ManyToManyField('Host', related_name='SD_hn_H',\
            blank=True, null=True)
    hostgroup_name = models.ManyToManyField('HostGroup', related_name='SD_hgn_HG',\
            blank=True, null=True)
    service_description = models.ForeignKey('Service', related_name='SD_s_S',\
            blank=True, null=True)
    inherits_parent = models.NullBooleanField(default=False)
    execution_failure_criteria = models.CharField(max_length=10)
    notification_failure_criteria = models.CharField(max_length=10)
    dependency_period = models.ForeignKey('TimePeriod', related_name='SD_dp_TP',\
            blank=True, null=True)

class ServiceEscalation(NagiosObject, models.Model):
    """Definition of the serviceescalation object.

    :class:`ServiceEscalation` has following :class:`django.db.models.ManyToManyField` attributes:
     - :attr:`host_name`
     - :attr:`hostgroup_name`

    :class:`ServiceEscalation` has following :class:`django.db.models.ForeignKey` attributes:
     - :attr:`service_description`
     - :attr:`escalation_period`

    """
    host_name = models.ManyToManyField('Host', related_name='SE_hn_H',\
            blank=True, null=True)
    hostgroup_name = models.ManyToManyField('HostGroup', related_name='SE_hgn_HG',\
            blank=True, null=True)
    service_description = models.ForeignKey('Service', related_name='SE_sd_S',\
            blank=True, null=True)
    contacts = models.ForeignKey(Contact)
    contactgroups = models.ForeignKey(ContactGroup)
    first_notification = models.IntegerField()
    last_notification = models.IntegerField()
    notification_interval = models.IntegerField()
    escalation_period = models.ForeignKey('TimePeriod', related_name='SD_ep_TP',\
            blank=True, null=True)
    escalation_options = models.CharField(max_length=10)

class HostDependency(NagiosObject, models.Model):
    dependent_host = models.ForeignKey('Host', related_name='HD_dh_H')
    dependent_hostgroup = models.ForeignKey('HostGroup', related_name='HD_dhg_hg')
    dependent_service = models.ForeignKey('Service', related_name='HD_ds_S')
    host_name = models.ForeignKey(Host)
    hostgroup_name = models.ForeignKey(HostGroup)
    inherits_parent = models.NullBooleanField()
    execution_failure_criteria = models.CharField(max_length=10)
    notification_failure_criteria = models.CharField(max_length=10)
    dependency_periode = models.ForeignKey(TimePeriod)

class HostEscalation(NagiosObject, models.Model):
    host_name = models.ForeignKey(Host, unique=True)
    hostgroup_name = models.ForeignKey(HostGroup)
    contacts = models.ForeignKey(Contact)
    contactgroups = models.ForeignKey(ContactGroup)
    first_notification = models.IntegerField()
    last_notification = models.IntegerField()
    notification_interval = models.IntegerField()
    escalation_period = models.ForeignKey(TimePeriod)
    escalation_options = models.CharField(max_length=10)

class CfgPath(models.Model):
    path = models.CharField(max_length=255,unique=True)

    @classmethod
    def get(self, criterion):
        try:
            o = CfgPath.objects.get(path=criterion)
            return o
        except CfgPath.DoesNotExist:
            o = CfgPath()
            o.path=criterion
            o.save()
            return o

    def __unicode__(self):
        return self.path

class NagiosCfg(NagiosObject, models.Model):
    '''Nagios main configuration file.
    We need the information of the file in the database, so we can
    fetch the default information
    '''
    FILE_NAME = 'nagios.cfg'
    server_name = models.CharField(max_length=255, default='localhost', unique=True)
    log_file = models.ForeignKey(CfgPath, related_name='NC_lf_CP',\
            default=lambda : CfgPath.get('/var/log/nagios/nagios.log').id)
    cfg_file = models.ManyToManyField(CfgPath, related_name='NC_cfg_file_CP',\
            blank=True,null=True)
    cfg_dir = models.ManyToManyField(CfgPath, related_name='NC_cfg_dir_CP',\
            blank=True,null=True)
    object_cache_file = models.ForeignKey(CfgPath, related_name='NC_ocf_CP',\
            default=lambda : CfgPath.get('/var/nagios/objects.cache').id)
    precached_object_file = models.ForeignKey(CfgPath, related_name='NC_pof_CP',\
            default=lambda : CfgPath.get('/var/nagios/objects.precache').id)
    resource_file = models.ForeignKey(CfgPath, related_name='NC_rf_CP',\
            default=lambda : CfgPath.get('/etc/nagios/resource.cfg').id)
    temp_file = models.ForeignKey(CfgPath, related_name='NC_tf_CP',\
            default=lambda : CfgPath.get('/var/nagios/nagios.tmp').id)
    temp_path = models.ForeignKey(CfgPath, related_name='NC_tp_CP',\
            default=lambda : CfgPath.get('/tmp').id)
    status_file = models.ForeignKey(CfgPath, related_name='NC_sf_CP',\
            default=lambda : CfgPath.get('/var/nagios/status.dat').id)
    status_update_interval = models.IntegerField(default=1)
    nagios_user = models.CharField(max_length=20, default='nagios')
    nagios_group = models.CharField(max_length=20, default='nagios')
    enable_notifications = models.NullBooleanField(blank=True,null=True)
    execute_service_checks = models.NullBooleanField(blank=True,null=True)
    accept_passive_service_checks = models.NullBooleanField(blank=True,null=True)
    execute_host_checks = models.NullBooleanField(blank=True,null=True)
    accept_passive_host_checks = models.NullBooleanField(blank=True,null=True)
    enable_event_handlers = models.NullBooleanField(blank=True,null=True)
    log_rotation_method = models.CharField(max_length=1, choices=LOG_ROTATION_METHODS, default='n')
    log_archive_path = models.ForeignKey(CfgPath, related_name='NC_laf_CP',\
            default=lambda : CfgPath.get('/var/log/nagios/archives').id)
    check_external_commands = models.NullBooleanField(blank=True,null=True)
    command_check_interval = models.IntegerField(default=1)
    command_file = models.ForeignKey(CfgPath, related_name='NC_cf_CP',\
            default=lambda : CfgPath.get('/var/nagios/rw/nagios.cmd').id)
    external_command_buffer_slots = models.IntegerField(default=512)
    check_for_updates = models.NullBooleanField(blank=True,null=True)
    bare_update_checks = models.NullBooleanField(default=False)
    lock_file = models.ForeignKey(CfgPath, related_name='NC_lckf_CP',\
            default=lambda : CfgPath.get('/var/nagios/rw/nagios.cmd').id)
    retain_state_information = models.NullBooleanField(blank=True,null=True)
    state_retention_file = models.ForeignKey(CfgPath, related_name='NC_srf_CP',\
            default=lambda : CfgPath.get('/var/nagios/retention.dat').id)
    retention_update_interval = models.IntegerField(default=60)
    use_retained_program_state = models.NullBooleanField(blank=True,null=True)
    use_retained_scheduling_info = models.NullBooleanField(blank=True,null=True)
    retained_host_attribute_mask = models.IntegerField(null=True)
    retained_service_attribute_mask = models.IntegerField(null=True)
    retained_process_host_attribute_mask = models.IntegerField(null=True)
    retained_process_service_attribute_mask = models.IntegerField(null=True)
    retained_contact_host_attribute_mask = models.IntegerField(null=True)
    retained_contact_service_attribute_mask = models.IntegerField(null=True)
    use_syslog = models.NullBooleanField(default=False)
    log_notifications = models.NullBooleanField(blank=True,null=True)
    log_service_retries = models.NullBooleanField(blank=True,null=True)
    log_host_retries = models.NullBooleanField(blank=True,null=True)
    log_event_handlers = models.NullBooleanField(blank=True,null=True)
    log_initial_states = models.NullBooleanField(default=False)
    log_external_commands = models.NullBooleanField(blank=True,null=True)
    log_passive_checks = models.NullBooleanField(blank=True,null=True)
    global_host_event_handler = models.CharField(max_length=255,blank=True,null=True)
    global_service_event_handler = models.CharField(max_length=255,blank=True,null=True)
    sleep_time = models.DecimalField(max_digits=4,decimal_places=2,default='0.25')
    # users can insert a choice or a proper value. This is why we keep it as a charfield
    service_inter_check_delay_method = models.CharField(max_length=6)
    max_service_check_spread = models.IntegerField(default=30)
    # service_interleave factor can be a number or s. keeping as char
    service_interleave_factor = models.CharField(max_length=2)
    max_concurrent_checks = models.IntegerField(default=0)
    check_result_reaper_frequency = models.IntegerField(default=10)
    max_check_result_reaper_time = models.IntegerField(default=60)
    check_result_path = models.ForeignKey(CfgPath, related_name='NC_crp_CP',\
            default=lambda : CfgPath.get('/var/nagios/spool/checkresults').id)
    max_check_result_file_age = models.IntegerField(default=3600)
    # users can insert a choice or a proper value. This is why we keep it as a charfield
    host_inter_check_delay_method = models.CharField(max_length=6)
    max_host_check_spread = models.IntegerField(default=30)
    interval_length = models.IntegerField(default=60)
    auto_reschedule_checks = models.NullBooleanField()
    auto_rescheduling_interval = models.IntegerField(default=30)
    auto_rescheduling_window = models.IntegerField(default=180)
    use_aggressive_host_checking = models.NullBooleanField(default=False)
    translate_passive_host_checks = models.NullBooleanField(default=False)
    passive_host_checks_are_soft = models.NullBooleanField(default=False)
    enable_predictive_host_dependency_checks = models.NullBooleanField(blank=True,null=True)
    enable_predictive_service_dependency_checks = models.NullBooleanField(blank=True,null=True)
    cached_host_check_horizon = models.IntegerField(default=15)
    cached_service_check_horizon = models.IntegerField(default=15)
    use_large_installation_tweaks = models.NullBooleanField(default=False)
    free_child_process_memory = models.NullBooleanField(blank=True,null=True)
    child_processes_fork_twice = models.NullBooleanField(blank=True,null=True)
    enable_environment_macros = models.NullBooleanField(blank=True,null=True)
    enable_flap_detection = models.NullBooleanField(blank=True,null=True)
    low_service_flap_threshold = models.DecimalField(max_digits=4,decimal_places=1,default='25.0')
    high_service_flap_threshold = models.DecimalField(max_digits=4,decimal_places=1,default='50.0')
    low_host_flap_threshold = models.DecimalField(max_digits=4,decimal_places=1,default='25.0')
    high_host_flap_threshold = models.DecimalField(max_digits=4,decimal_places=1,default='50.0')
    soft_state_dependencies = models.NullBooleanField(default=False)
    service_check_timeout = models.IntegerField(default=60)
    host_check_timeout = models.IntegerField(default=60)
    event_handler_timeout = models.IntegerField(default=60)
    notification_timeout = models.IntegerField(default=60)
    ocsp_timeout = models.IntegerField(default=5)
    ochp_timeout = models.IntegerField(default=5)
    perfdata_timeout = models.IntegerField(default=5)
    obsess_over_services = models.NullBooleanField(default=False)
    ocsp_command = models.ForeignKey(Command, related_name='NC_ocsp_com_C', blank=True,null=True)
    obsess_over_hosts = models.NullBooleanField(default=False)
    ochp_command = models.ForeignKey(Command, related_name='NC_ochp_com_C', blank=True,null=True)
    process_performance_data = models.NullBooleanField(default=False)
    host_perfdata_command = models.ForeignKey(CheckCommand, related_name='NC_h_perfdata_com_CC', blank=True,null=True)
    service_perfdata_command = models.ForeignKey(CheckCommand, related_name='NC_s_perfdata_com_CC', blank=True,null=True)
    host_perfdata_file = models.CharField(max_length=255, blank=True, null=True)
    service_perfdata_file = models.CharField(max_length=255, blank=True, null=True)
    host_perfdata_file_template = models.CharField(max_length=255, \
            default="[HOSTPERFDATA]\t$TIMET$\t$HOSTNAME$\t$HOSTEXECUTIONTIME$\t$HOSTOUTPUT$\t$HOSTPERFDATA$",\
            blank=True,null=True)
    service_perfdata_file_template = models.CharField(max_length=255, \
            default="[SERVICEPERFDATA]\t$TIMET$\t$HOSTNAME$\t$SERVICEDESC$\t$SERVICEEXECUTIONTIME$\t$SERVICELATENCY$\t$SERVICEOUTPUT$\t$SERVICEPERFDATA$",\
            blank=True,null=True)
    host_perfdata_file_mode = models.CharField(max_length=1, choices=OPEN_FILE_MODES,\
            blank=True,null=True)
    service_perfdata_file_mode = models.CharField(max_length=1, choices=OPEN_FILE_MODES,\
            blank=True,null=True)
    host_perfdata_file_processing_interval = models.IntegerField(default=60,\
            blank=True,null=True)
    service_perfdata_file_processing_interval = models.IntegerField(default=60,\
            blank=True,null=True)
    host_perfdata_file_processing_command = models.ForeignKey(CheckCommand, related_name='NC_hpfpc_CC',\
            blank=True,null=True,db_column='hpfpc')
    service_perfdata_file_processing_command = models.ForeignKey(CheckCommand, related_name='NC_spfpc_CC',\
            blank=True,null=True,db_column='spfpc')
    check_for_orphaned_services = models.NullBooleanField(blank=True,null=True)
    check_for_orphaned_hosts = models.NullBooleanField(blank=True,null=True)
    check_service_freshness = models.NullBooleanField(blank=True,null=True)
    service_freshness_check_interval = models.IntegerField(default=60,\
            blank=True,null=True)
    check_host_freshness = models.NullBooleanField(blank=True,null=True)
    host_freshness_check_interval = models.IntegerField(default=60,\
            blank=True,null=True)
    additional_freshness_latency = models.IntegerField(default=15)
    enable_embedded_perl = models.NullBooleanField(blank=True,null=True)
    use_embedded_perl_implicitly = models.NullBooleanField(blank=True,null=True)
    date_format = models.CharField(max_length=10)
    use_timezone = models.CharField(max_length=100, default='Europe/Brussels')
    illegal_object_name_chars = models.CharField(max_length=255,\
            default="`~!$%^&*|'\"<>?,()=")
    illegal_macro_output_chars = models.CharField(max_length=255,\
            default="~$^&\"|'<>")
    use_regexp_matching = models.NullBooleanField(blank=True,null=True)
    use_true_regexp_matching = models.NullBooleanField(default=False)
    admin_email = models.EmailField(default='djagios@localhost.local')
    admin_pager = models.CharField(max_length=75, default='djagios@pager.localhost.local')
    event_broker_options = models.IntegerField(default=-1)
    debug_file = models.CharField(max_length=255)
    # debug level should be a logical OR!
    debug_level = models.IntegerField(default=0)
    debug_verbosity = models.IntegerField(default=1, \
            choices=(('0','basic'),('1','detailed'),('1','extreme')))
    max_debug_file_size = models.IntegerField(default=1000000)
    p1_file = models.ForeignKey(CfgPath, related_name='NC_p1f_CP',\
            default=lambda : CfgPath.get('/usr/bin/p1.pl').id)
    daemon_dumps_core = models.NullBooleanField(default=False)
    bare_update_check = models.NullBooleanField(default=False)

    def __unicode__(self):
        return self.server_name

    def parse_to_nagios_cfg(self, path=None):
        """:func:`parse_to_nagios_cfg` will create a nagios formatted block of the
        current :class:`NagiosCfg` object.

        :param path: Optional, allows to pass the dir where the file will be written.
        :type path: :class:`str`
        :rtype: :class:`str`
        :raises: :Exc:`djagios.core.exceptions.ParseError`

        """
        s = StringIO.StringIO()
        s.write("# Nagios configuration for %s\n# Generated by Djagios.\n"%self.server_name)
        # log_file is always the first item!!!!
        s.write('log_file=%s\n'%self.log_file)

        s.write('cfg_dir=%s\n'%(os.path.join(path, 'objects')))
        for attr in self._meta.get_all_field_names():
            if not hasattr(self, attr) or attr == 'id':
                continue
            # attributes to ignore
            if attr in ('cfg_dir', 'cfg_file', 'server_name',\
                    'log_file','bare_update_checks',):
                continue
            value = getattr(self, attr)
            if isinstance(value, str) and not value:
                continue
            if isinstance(value, (str,int, unicode, bool,\
                    CfgPath,)):
                s.write('%s=%s\n'%(attr,value))
        s.flush()
        ret = s.getvalue()
        s.close()
        return ret

####################################################
# Models for the website and the configuration help.
####################################################

class HostTemplate(models.Model):
    """:class:`HostTemplate` is a helper class for Djagios website.
    This class will allow us to assign service, servicegroups, contact
    and contactgroups to the Host.
    These can be created by the admins, and only selected by the users.
    obsolete!!!!!
    """
    name = models.CharField(max_length=255, unique=True)
    use = models.ForeignKey(Host, related_name='HT_use_H')
    services = models.ManyToManyField(Service, related_name='HT_s_S',\
            blank=True,null=True)
    contacts = models.ManyToManyField(Contact, related_name='HT_c_C',\
            blank=True,null=True)
    contact_groups = models.ManyToManyField(ContactGroup, related_name='HT_cg_CG',\
            blank=True,null=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

class HostTemplateForm(forms.ModelForm):
    pass
    class Meta:
        model = HostTemplate

class HostForm(forms.Form):
    name = forms.CharField(label='Server Name', max_length=50)
    address = forms.CharField(label='Servers Address (dns or IP)', max_length=50)
    template = forms.ModelChoiceField(label='Template', queryset=Host.objects.filter(register=False).order_by('name'))

class HostToServiceForm(forms.Form):
    service = forms.ModelChoiceField(label='Service', queryset=Service.objects.exclude(register=False).order_by('service_description'))
    host = forms.ModelChoiceField(label='Host', queryset=Host.objects.exclude(register=False).order_by('host_name'))

class HostFromServiceForm(forms.Form):
    host = forms.ModelChoiceField(label='Host', queryset=Host.objects.exclude(register=False).order_by('host_name'))
    service = forms.ModelChoiceField(Service.objects.exclude(register=False), widget=forms.Select(attrs={'disabled': 'True'}, choices=(('-1', 'Select Host'),)))

class HostDeleteForm(forms.Form):
    host = forms.ModelChoiceField(label='Host', queryset=Host.objects.exclude(register=False).order_by('host_name'))
    sure = forms.BooleanField(label='Check if you are sure', required=True)

