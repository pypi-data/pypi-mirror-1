#!/usr/bin/python
# 
# Djagios import tool
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

import fileinput
import uuid
import re
import os
import sys
import logging

from django.core.management import setup_environ
import settings
from django.db import models
from djagios.core import models
from djagios.core.models import *

__version__ = '0.1'
setup_environ(settings)
LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

block_pattern = "define\s+(?P<def_type>\S*)\s*\{\n*(?P<content>.*?)\}"
attrib_pattern = '\s*(?P<attrib>\S+)\s+(?P<value>.*)'
class NagiosConfigParser():
    '''
    Parser for Nagios Configuration files.

    Parsing is done in multiple steps.
    1) parse main configuration file
    2) parse separate config files and write out to standard files
    3) parse the standard files following a correct order
    4) all objects that cannot be put in the db write out again
        redo this step until the object is empty
    5) remove standard files (if -d is not given)
    '''

    hosts = dict()
    host_groups = dict()
    services = dict()
    service_groups = dict()
    contacts = dict()
    contact_groups = dict()
    def __init__(self):
        logging.debug('NagiosConfigParser.__init__() called')
        # temp folder where we will put our config files
        self.tmp_path = os.path.join('/tmp/', str(uuid.uuid4()))
        # create folder of tmp_path
        try:
            os.mkdir(self.tmp_path)
            logging.info('Temporary directory %s created for the parsed config files'%self.tmp_path)
        except:
            logging.critical('Cannot create %s, exiting!'%self.tmp_path)
            sys.exit(1)
        logging.info('NagiosConfigParser initialized!')

    def write_object(self, key, value):
        '''Write the data to the correct file.'''
        text = '''define %s {
%s
}
'''
        logging.debug('opening %s/%s.cfg'%(self.tmp_path, key))
        file = open('%s/%s.cfg'%(self.tmp_path,key), 'a')
        file.write(text%(key,value))
        file.flush()
        file.close()
        logging.debug('closing %s/%s.cfg'%(self.tmp_path, key))

    def sanitize(self, path):
        s = self._get_file_content(path)
        fd = open(path, 'w')
        for line in s.splitlines():
            if not line.strip():
                continue
            if re.compile('^\s*#').search(line):
                continue
            fd.write('%s\n'%line)
        fd.flush()
        fd.close()

    def parse_config(self, path):
        ''' Parsing object file and writing out to correct
        file in temp dir.
        '''
        fd  = open(path, 'r')
        s = fd.read()
        s = s.replace('\\\n','')
        mo = re.findall("define\s+(?P<def_type>\S*)\s*\{\n*(?P<content>.*?)\}", s, re.S)
        for key,value in mo:
            self.write_object(key, value)
        fd.close()

    def parse_main(self,server_name,path):
        ''' Parse the main nagios configuration.

        This will allow us to fetch all the needed configuration
        setting and files.
        '''
        nc = None
        try: 
            nc = NagiosCfg.objects.get(server_name=server_name)
        except NagiosCfg.DoesNotExist:
            nc = NagiosCfg()
            nc.server_name=server_name
            nc.save()
        print "Initial save happend!\n"
        # open the nagios_file
        for line in fileinput.input(path):
            if not line.strip():
                continue
            if re.compile('^#').search(line):
                continue
            res = line.split('=', 1)
            # certain attributes are in fact foreign keys.
            # So first check whether the entry belongs to one of them.
            path = CfgPath()
            logging.debug('setting %s to  %s'%(res[0],res[1].strip()))
            paths_list = ('cfg_dir', 'cfg_file', 'log_file', 'object_cache_file' ,\
                    'precached_object_file', 'resource_file', 'temp_file',\
                    'temp_path', 'status_file', 'command_file', 'log_archive_path',\
                    'check_result_path','state_retention_file', 'lock_file', 'p1_file',
                    )
            if res[0] in paths_list:
                path = CfgPath.get(res[1].strip())
                #cfg_dir is manytomany and setattr will fail
                if res[0] == 'cfg_dir':
                    nc.cfg_dir.add(path)
                    continue
                #cfg_file is manytomany and setattr will fail
                if res[0] == 'cfg_file':
                    nc.cfg_file.add(path)
                    continue
                setattr(nc, res[0], path)
                continue
            if isinstance(nc._meta.get_field_by_name(res[0])[0],\
                models.NullBooleanField):
                if res[1].strip() == '1':
                    setattr(nc, res[0], True)
                else:
                    setattr(nc, res[0], False)
                continue

            setattr(nc, res[0], res[1].strip())
        nc.save()
        fileinput.close()
        print "Nagios main config imported, starting with the other objects"

    def _delete_all_objects(self, o):
        '''Delete all objects from database.
        how to run manage.py reset core?'''
        pass

    def _get_file_content(self,filename,delete=True):
        file = open(filename, 'r')
        s = file.read()
        file.close()
        os.remove(filename)
        logging.debug('removed %s, filling up with failed objects'%filename)
        return s

    def write_queue(self, filename, key, val):
        block = 'define %s {\n%s\n}\n'%(key,val)
        queue = open(filename, 'a')
        queue.write(block)
        queue.flush()
        queue.close()

    def import_command_to_db(self):
        filename = os.path.join(self.tmp_path, 'command.cfg')
        s = self._get_file_content(filename)
        logging.debug('Cleaning out the Command objects from db.')
        self._delete_all_objects(Command)
        logging.debug('Finished cleaning the Command objects from db.')

        mo = re.findall(block_pattern, s, re.S)
        for key,val in mo:
            o = Command()
            #we have our block, so read line per line and parse the block
            logging.debug('got "%s"'%val.strip())
            for line in val.strip().splitlines():
                if not line:
                    continue
                logging.debug('Parsing line %s'%line)
                m = re.search(attrib_pattern, line, re.I)
                rdict = m.groupdict()
                attrib = rdict['attrib'].strip()
                value = rdict['value'].strip().split(';')[0]
                if hasattr(o,attrib):
                    setattr(o, attrib, value)
            try:
                o.save()
            except:
                self.write_queue(filename, key, value)

    def import_contact_to_db(self,name):
        logging.debug('starting contact import %s'%name)

        # list of all the TimePeriod keys
        TP_KEYS = ('host_notification_period', 'service_notification_period')
        C_KEYS = ('host_notification_commands', 'service_notification_commands')
        o = Contact()
        o.save()
        #we have our block, so read line per line and parse the block
        for attrib,value in self.contacts[name].iteritems():
            if hasattr(o,attrib):
                if attrib == 'contactgroups':
                    try:
                        o.contactgroups.add(ContactGroup.get(value))
                        continue
                    except Contact.DoesNotExist:
                        self.write_queue(filename, key, val)
                        continue
                if attrib == 'use':
                    try:
                        o.use = Contact.get(value)
                    except Contact.DoesNotExist:
                        self.import_contact_to_db(value)
                        o.use = Contact.get(value)
                    continue
                if attrib in TP_KEYS:
                    try:
                        setattr(o, attrib, TimePeriod.get(value))
                        continue
                    except TimePeriod.DoesNotExist:
                        self.write_queue(filename, key, val)
                        continue
                if attrib == 'host_notification_commands':
                    try:
                        o.host_notification_commands.add(CheckCommand.get(value))
                        continue
                    except Contact.DoesNotExist:
                        self.write_queue(filename, key, val)
                        continue
                if attrib == 'service_notification_commands':
                    try:
                        o.service_notification_commands.add(CheckCommand.get(value))
                        continue
                    except Contact.DoesNotExist:
                        self.write_queue(filename, key, val)
                        continue
                if isinstance(o._meta.get_field_by_name(attrib)[0],\
                    models.NullBooleanField):
                    if value == '1':
                        setattr(o, attrib, True)
                    else:
                        setattr(o, attrib, False)
                    continue
                setattr(o, attrib, value)

            try:
                o.save()
            except Exception, e:
                logging.debug('Cannot save: %s'%str(e))

    def import_contact_group_to_db(self, name):
        logging.debug('starting contactgroup import %s'%name)
        o = ContactGroup()
        o.save()
        for attrib,value in self.contact_groups[name].iteritems():
            if attrib == 'members':
                for v in value.split(','):
                    o.members.add(Contact.get(v))
                continue
            if attrib == 'contactgroup_members':
                o.members.add(ContactGroup.get(value))
                continue
            if hasattr(o,attrib):
                setattr(o, attrib, value)
        if o.contactgroup_name:
            o.save()
        else:
            ContactGroup.delete(o)
        logging.debug('finished contactgroup import %s'%name)

    def import_timeperiod_to_db(self):
        '''Separate class as the time period needs to
        be able to create timeranges.
        WIth other classes we can find out what class is
        excpected and first fetch or create it. Timerange has
        dynamic attributes.
        '''
        logging.debug('fetching timerange objects')
        filename = os.path.join(self.tmp_path, 'timeperiod.cfg')
        s = self._get_file_content(filename)
        logging.debug('removed %s, filling up with failed objects'%filename)
        self._delete_all_objects(TimePeriod)
        self._delete_all_objects(TimeRange)
        logging.debug('Finished cleaning the TimePeriod and TimeRange objects from db.')
        mo = re.findall(block_pattern, s, re.S)
        for key,val in mo:
            o = TimePeriod()
            o.save()
            for line in val.strip().splitlines():
                if not line:
                    continue
                logging.debug('parse ATTRLINE: %s'%line.strip())
                m = re.search(attrib_pattern, line.strip(), re.I)
                rdict = m.groupdict()
                logging.debug(rdict)
                if hasattr(o,rdict['attrib']):
                    if rdict['attrib'] == 'exclude':
                        o.exclude.add(get_timeperiod(rdict['value'].strip().split(';')[0]))
                        continue
                    setattr(o,rdict['attrib'], rdict['value'].split(';')[0])
                else:
                    # attribute not found, thus it must be a timeframe
                    tr =TimeRange.get(rdict['attrib'], rdict['value'].split(';')[0])
                    o.ranges.add(tr)
            o.save()

    def import_final_objects(self):
        '''Here we will import hosts, hostgroups, services and servicegroups.
        This due to the fact that they are all dependent on each other'''

        # call the parser that adds the type to global dict.
        logging.info('Starting with host.cfg')
        self.parse_to_dict(os.path.join(self.tmp_path, 'host.cfg'))
        logging.info('Finished with host.cfg')
        logging.info('Starting with hostgroup.cfg')
        self.parse_to_dict(os.path.join(self.tmp_path, 'hostgroup.cfg'))
        logging.info('Finished with hostgroup.cfg')
        logging.info('Starting with service.cfg')
        self.parse_to_dict(os.path.join(self.tmp_path, 'service.cfg'))
        logging.info('Finished with service.cfg')
        logging.info('Starting with servicegroup.cfg')
        self.parse_to_dict(os.path.join(self.tmp_path, 'servicegroup.cfg'))
        logging.info('Finished with servicegroup.cfg')
        logging.info('Starting with contactgroup.cfg')
        self.parse_to_dict(os.path.join(self.tmp_path, 'contactgroup.cfg'))
        logging.info('Finished with contactgroup.cfg')
        logging.info('Starting with contact.cfg')
        self.parse_to_dict(os.path.join(self.tmp_path, 'contact.cfg'))
        logging.info('Finished with contact.cfg')

        for c in self.contacts:
            self.import_contact_to_db(c)
        for cg in self.contact_groups:
            self.import_contact_group_to_db(cg)

        # start running over the host dict and import one by one
        for h in self.hosts:
            self.import_host_to_db(h)
        for hg in self.host_groups:
            self.import_hostgroup_to_db(hg)
        # we now do the final_stage which will also add the hostgroups
        # the other values are updated untill we fix it up
        for h in self.hosts:
            self.import_host_to_db(h, final_stage=True)
        for s in self.services:
            self.import_service_to_db(s)
        for sg in self.service_groups:
            self.import_servicegroup_to_db(sg)
        # we now do the final_stage which will also add the servicegroups
        # the other values are updated untill we fix it up
        for s in self.services:
            self.import_service_to_db(s)

    def parse_to_dict(self, filename):
        if not os.path.exists(filename):
            return
        s = self._get_file_content(filename)
        mo = re.findall(block_pattern, s, re.S)
        for key,val in mo:
            d = dict()
            for line in val.strip().splitlines():
                if not line or line.startswith('#'):
                    continue
                if re.match('\s*;.*', line):
                    continue
                m = re.search(attrib_pattern, line.strip(), re.I)
                rdict = m.groupdict()
                attrib = rdict['attrib'].strip()
                value = rdict['value'].split(';')[0].strip()
                d[attrib]=value
            logging.debug('d = %s'%d)
            if key == 'host':
                if 'host_name' in d:
                    self.hosts[d['host_name']]=d
                elif 'name' in d:
                    self.hosts[d['name']]=d
                continue
            if key == 'hostgroup':
                self.host_groups[d['hostgroup_name']]=d
                continue
            if key == 'service':
                if 'service_description' in d:
                    self.services[d['service_description']]=d
                elif 'name' in d:
                    self.services[d['name']]=d
                continue
            if key == 'servicegroup':
                self.service_groups[d['servicegroup_name']]=d
                continue
            if key == 'contactgroup':
                self.contact_groups[d['contactgroup_name']]=d
                continue
            if key == 'contact':
                if 'contact_name' in d:
                    self.contacts[d['contact_name']]=d
                elif 'name' in d:
                    self.contacts[d['name']]=d
                continue

    def import_hostgroup_to_db(self, name):
        logging.debug('starting hostgroup import %s'%name)
        o = HostGroup()
        o.save()
        for attrib,value in self.host_groups[name].iteritems():
            logging.debug('attrib: %s, value: %s'%(attrib, str(value)))
            if hasattr(o,attrib):
                if attrib == 'members':
                    for host in value.split(','):
                        logging.debug('found member: %s'%host.strip())
                        try:
                            h = Host.get(host.strip())
                            o.members.add(h)
                        except Host.DoesNotExist:
                            self.import_host_to_db(host.strip())
                            o.members.add(host.strip())
                    continue
                if attrib == 'hostgroup_members':
                    for hg in value.split(','):
                        logging.debug('found hostgroup_ member: %s'%host)
                        hg = hg.strip()
                        try:
                            h = HostGroup.get(hg)
                            o.hostgroup_members.add(HostGroup.get(hg))
                        except HostGroup.DoesNotExist:
                            self.import_hostgroup_to_db(hg)
                            o.hostgroup_members.add(HostGroup.get(hg))
                    continue
                setattr(o,attrib, value)
            o.save()
        logging.debug('finished hostgroup import %s'%name)

    def import_host_to_db(self, name,final_stage=False):
        logging.debug('starting host import %s'%name)
        try:
            o = Host.get(name)
        except Host.DoesNotExist:
            o = Host()
            o.name=name
            o.save()
            o.name=None
        for attrib,value in self.hosts[name].iteritems():
            logging.debug('attrib: %s, value: %s'%(attrib, str(value)))
            if attrib == 'use':
                try:
                    setattr(o, attrib, Host.get(value))
                    continue
                except Host.DoesNotExist:
                    self.import_host_to_db(value)
                    setattr(o, attrib, Host.get(value))
                    continue
            if attrib == 'parents':
                for h in value.split(','):
                    try:
                        o.parents.add(Host.get(h))
                        continue
                    except Host.DoesNotExist:
                        self.import_host_to_db(h)
                        o.parents.add(Host.get(h))
                        continue
                continue
            if attrib == 'hostgroups':
                if final_stage:
                    for hg in value.split(','):
                        try:
                            o.hostgroups.add(HostGroup.get(hg))
                            continue
                        except HostGroup.DoesNotExist:
                            self.import_hostgroup_to_db(value)
                            o.hostgroups.add(HostGroup.get(value))
                            continue
                    continue
                else:
                    continue
            if attrib == 'contacts':
                o.contacts.add(Contact.get(value))
                continue
            if attrib == 'contact_groups':
                o.contact_groups.add(ContactGroup.get(value))
                continue
            if attrib == 'notification_period':
                setattr(o, attrib, TimePeriod.get(value))
                continue
            if attrib == 'check_command':
                setattr(o, attrib, CheckCommand.get(value))
                continue
            if attrib == 'check_period':
                setattr(o, attrib, TimePeriod.get(value))
                continue
            if attrib == 'event_handler':
                setattr(o, attrib, CheckCommand.get(value))
                continue
            if hasattr(o,attrib):
                if isinstance(o._meta.get_field_by_name(attrib)[0],\
                        models.NullBooleanField):
                    if value == '1':
                        setattr(o, attrib, True)
                    else:
                        setattr(o, attrib, False)
                    continue
                setattr(o, attrib, value)
            elif not attrib.startswith('_'):
                raise RuntimeError('ERROR: Attribute %s with value "%s" not found'%(attrib,value))
        o.save()
        logging.debug('finished host import %s'%name)

    def import_service_to_db(self,name,final_stage=False):
        logging.debug('starting service import %s'%name)
        try:
            o = Service.get(name)
            return
        except Service.DoesNotExist:
            o = Service()
            o.service_description=name
            o.save()
            o.service_description=None
        for attrib,value in self.services[name].iteritems():
            logging.debug('attrib: %s, value: %s'%(attrib, str(value)))
            if attrib == 'use':
                try:
                    o.use = Service.get(value)
                    continue
                except Service.DoesNotExist:
                    self.import_service_to_db(value)
                    o.use = Service.get(value)
                    continue
            if attrib == 'host_name':
                for h in value.split(','):
                    if h.startswith('!'):
                        o.host_name_n.add(Host.get(h.strip()[1:]))
                    else:
                        o.host_name.add(Host.get(h.strip()))
                continue
            if attrib == 'hostgroup_name':
                for hg in value.split(','):
                    if hg.startswith('!'):
                        o.hostgroup_name_n.add(HostGroup.get(hg.strip()[1:]))
                    else:
                        o.hostgroup_name.add(HostGroup.get(hg.strip()))
                continue
            if attrib == 'servicegroups':
                if final_stage:
                    for sg in value.split(','):
                        try:
                            o.servicegroups.add(ServiceGroup.get(sg))
                            continue
                        except ServiceGroup.DoesNotExist:
                            self.import_servicegroups_to_db(sg)
                            o.servicegroups.add(ServiceGroup.get(sg))
                            continue
                else:
                    continue
            if attrib == 'contacts':
                o.contacts.add(Contact.get(value))
                continue
            if attrib == 'contact_groups':
                o.contact_groups.add(ContactGroup.get(value))
                continue
            if attrib == 'notification_period':
                setattr(o, attrib, TimePeriod.get(value))
                continue
            if attrib == 'check_command':
                setattr(o, attrib, CheckCommand.get(value))
                continue
            if attrib == 'check_period':
                setattr(o, attrib, TimePeriod.get(value))
                continue
            if attrib == 'event_handler':
                setattr(o, attrib, CheckCommand.get(value))
                continue
            if hasattr(o,attrib):
                if isinstance(o._meta.get_field_by_name(attrib)[0],\
                        models.NullBooleanField):
                    if value == '1':
                        setattr(o, attrib, True)
                    else:
                        setattr(o, attrib, False)
                    continue
                setattr(o, attrib, value)
            elif not attrib.startswith('_'):
                raise RuntimeError('ERROR: Attribute %s with value "%s" not found'%(attrib,value))
        try :
            o.save()
        except:
            logging.error('Could not save service %s!!!'%o.service_description)
        logging.debug('finished Service import %s'%name)

    def import_servicegroup_to_db(self, name):
        logging.debug('starting servicegroup import %s'%name)
        o = ServiceGroup()
        o.save()
        for attrib,value in self.service_groups[name].iteritems():
            logging.debug('attrib: %s, value: %s'%(attrib, str(value)))
            if hasattr(o,attrib):
                if attrib == 'members':
                    for s in value.split(','):
                        logging.debug('found member: %s'%s.strip())
                        try:
                            s = Service.get(s.strip())
                            o.members.add(s)
                        except Host.DoesNotExist:
                            self.import_host_to_db(s.strip())
                            o.members.add(Service.get(s))
                    continue
                if attrib == 'servicegroup_members':
                    for sg in value.split(','):
                        logging.debug('found servicegroup_member: %s'%host)
                        sg = sg.strip()
                        try:
                            s = ServiceGroup.get(sg)
                            o.servicegroup_members.add(ServiceGroup.get(sg))
                        except ServiceGroup.DoesNotExist:
                            self.import_servicegroup_to_db(sg)
                            o.servicegroup_members.add(ServiceGroup.get(sg))
                    continue
                setattr(o,attrib, value)
            o.save()
        logging.debug('finished servicegroup import %s'%name)

    def get_config_files(self, path):
        """method to fetch all files in a certain path"""
        dirlist = os.listdir(path)
        reslist = set()
        for file in dirlist:
            abs_file = os.path.join(path, file)
            if os.path.isfile(abs_file) \
                    and abs_file.endswith('cfg'):
                    reslist.add(abs_file)
            elif os.path.isdir(abs_file):
                reslist.update(self.get_config_files(abs_file))

        return reslist


    def import_config(self,server_name,path):
        '''Imports the config files fetched from the nagios.cfg file
        and parses all objects to a file per object type.
        This will allow us to import the the different files without
        having key issues.
        '''
        self.parse_main(server_name, path)
        nc = NagiosCfg.objects.get(server_name=server_name)

        for path in nc.cfg_dir.values():
            logging.debug('Found %s as cfg_dir path'%(path['path']))
            if os.path.isdir(path['path']):
                dirlist = self.get_config_files(path['path'])
                for file in dirlist:
                    if file.endswith('.cfg'):
                        logging.debug('Found %s as nagios config file'%file)
                        logging.debug('Sanitizing the config file first')
                        self.sanitize(file)
                        self.parse_config(file)

        for path in nc.cfg_file.values():
            if os.path.isfile(path['path']) \
                    and path['path'].endswith('.cfg'):
                logging.debug('Found %s as nagios config file'%path)
                logging.debug('Sanitizing the config file first')
                self.sanitize(path['path'])
                logging.debug('parsing the config file')
                self.parse_config(path['path'])
        # import the files into objects and db
        self.import_command_to_db()
        self.import_timeperiod_to_db()
        self.import_final_objects()

        # remove the temp dir! TODO
        os.rmdir(self.tmp_path)

if __name__ == '__main__':
    from optparse import OptionParser, make_option
    option_list = [
        make_option("-s", "--server_name",
                    action="store", dest="server_name",
                    default='localhost',
                    help="Submit the server name for the config"),
        make_option("-p", "--path",
                    action="store", dest="path",
                    default='/etc/nagios/nagios.cfg',
                    help="Path of the main configuration file."),
        make_option("-d", "--debuglevel",
                    action="store", dest="debuglevel",
                    default="info",
                    help="Level of debugging can be any of \
                            (debug,info,warning, error or critical)")
        ]
    parser = OptionParser(usage="python %prog [options]",
                        version=__version__,
                        description="An import tool for adding an existing nagios configuration to Djagios.",
                        option_list=option_list)
    (options,args) = parser.parse_args()
    level = LEVELS.get(options.debuglevel, logging.NOTSET)
    logging.basicConfig(level=level)
    ncp = NagiosConfigParser()
    ncp.import_config(options.server_name, options.path)

