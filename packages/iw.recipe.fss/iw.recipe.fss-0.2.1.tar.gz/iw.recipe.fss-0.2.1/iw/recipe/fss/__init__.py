# -*- coding: utf-8 -*-
# Copyright (C)2007 'Ingeniweb'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""Recipe fss"""
import os
from warnings import warn

class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        bin_dir = buildout['buildout']['bin-directory']
        # XXX this is a bit hacky, see how we can get the var folder in a cleany
        # way
        self.var = os.path.join(os.path.split(bin_dir)[0], 'var')
        self.conf_paths = []

        if 'conf' in options:
            self.conf_paths.append(options['conf'])
            warn("Use 'zope-instances' parameters instead of 'conf'",
                 DeprecationWarning, stacklevel=2)

        elif 'zope-instances' in options:
            for dir_path in options['zope-instances'].strip().split('\n'):
                # directories are not created before the install step then
                # it is not possible to make any exitence check here
                self.conf_paths.append(os.path.join(dir_path.strip(), 'etc',
                                                    'plone-filesystemstorage.conf'))

        else:
            # Nor 'conf' neither 'zope-instances' parameters are defined.
            # We try to find classic zope instance names in the local
            # configuration file.
            if 'instance' in buildout:
                instance_location = buildout['instance']['location']
            elif 'zopeinstance' in buildout:
                instance_location = buildout['zopeinstance']['location']
            else:
                raise KeyError("The system is unable to find a Zope instance. "
                               "Please use the zope-instance parameter.")

            self.conf_paths.append(os.path.join(instance_location, 'etc',
                                                'plone-filesystemstorage.conf'))
        # reading the storages

        def _read_storage_line(line):
            line = line.strip().split(' ')
            name = line[0]
            site = line[1]

            # optional parameters
            if len(line) > 2:
                strategy = line[2]
            else:
                strategy = 'directory'

            if len(line) > 3:
                storage = line[3]
            else:
                storage = os.path.join(self.var, 'fss_storage_%s' % name)

            if len(line) > 4:
                backup = line[4]
            else:
                backup = os.path.join(self.var, 'fss_backup_%s' % name)

            return name, site, strategy, storage, backup

        self.storages = [_read_storage_line(st) for st in
                         options['storages'].strip().split('\n')]

    def install(self):
        """installer"""
        # FSS needs two things for each storage:
        #  - create two directories (storage and backup)
        #  - create a plone-filesystemstorage.conf file
        conf_content = []

        main_template = ("# main storage %(name)s for %(site)s\n"
                         "storage-path %(storage)s\n"
                         "backup-path %(backup)s\n"
                         "storage-strategy %(strategy)s\n\n")

        template = ("# storage %(name)s\n"
                    "<site %(site)s>\n"
                    " storage-path %(storage)s\n"
                    " backup-path %(backup)s\n"
                    " storage-strategy %(strategy)s\n"
                    "</site>\n\n")

        first = True

        for name, site, strategy, storage, backup in self.storages:
            # create two directories
            for path in (storage, backup):
                if os.path.exists(path):
                    continue
                os.makedirs(path)

            # create the conf file
            if first:
                tpl = main_template
                first = False
            else:
                tpl = template

            conf_content.append(tpl % {'name': name, 'site': site,
                                       'strategy': strategy,
                                       'storage': storage,
                                       'backup': backup})

        if len(self.conf_paths) > 0:
            for conf_path in self.conf_paths:

                etc = open(conf_path, 'w')
                try:
                    etc.write('# FSS conf file generated by iw.recipe.fss\n\n')
                    for conf in conf_content:
                        etc.write(conf)
                finally:
                    etc.close()

            # returns installed files
            return tuple(self.conf_paths)

        else:
            raise KeyError('No filesystem path found in configuration')

    update = install
