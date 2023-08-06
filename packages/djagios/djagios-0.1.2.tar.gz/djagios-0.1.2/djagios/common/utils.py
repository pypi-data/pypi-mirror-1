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

import os
import sys
import logging

from djagios.core.models import *

class Exporter():
    """Exporter provides the functionality to export the different objects to the correct format
    used by Nagios.
    This tool will have to be adapted each time the configuration format of Nagios changes.
    """

    def _write_file(self, content, path):
        """Internal function that will write out the string to a file.
        """
        logging.debug("Exporter._write_file: opening %s"%path)
        if os.path.exists(path) and not os.path.isfile(path):
            logging.error("Exporter._write_file: %s is not a file"%path)
            return
        file = open(path, 'a')
        file.write(content)
        file.flush()
        file.close()
        logging.debug("Exporter._write_file: closed %s"%path)

    def export(self, path):
        """export will run over all objects and export them one by one to the specified 
        path. Here they will be ordered per objecttype.
        The export is not recursive.

        :param path: containing the location where to put the cfg files, **must be a directory**
        :type path: :class:`str`
        """
        if not os.path.isdir(path):
            raise ValueError('given path %s is not a directory!'%path)

        # creating the objects dir
        os.mkdir(os.path.join(path, 'objects'))

        OBJECT_LIST = (Host, HostGroup, Service, ServiceGroup, Command, TimePeriod,\
                Contact, ContactGroup,)
        for o in OBJECT_LIST:
            for obj in o.objects.all():
                self.export_object(obj, os.path.join(path, 'objects'))
        self.export_object(NagiosCfg.objects.all()[0], path)

    def export_object(self, nagios_obj, path):
        """:func:`export_object` will open a file (with the name of the object type)
        and write the content of the object to it.

        To do that It depends on the export function defined in the model class.

        :param nagios_obj: object that should be written as a nagios config object
        :type nagios_obj: :class:`djagios.core.models.NagiosObject`
        :param path: containing the location of the configfiles.
        :type path: :class:`str`
        """
        if not isinstance(nagios_obj, NagiosObject):
            raise RuntimeError('object received is not a NagiosObject')
        if os.path.isfile(path):
            self._write_file(nagios_obj.parse_to_nagios_cfg(), path)
        elif os.path.isdir(path):
            p = os.path.join(path, nagios_obj.FILE_NAME)
            self._write_file(nagios_obj.parse_to_nagios_cfg(path), p)

