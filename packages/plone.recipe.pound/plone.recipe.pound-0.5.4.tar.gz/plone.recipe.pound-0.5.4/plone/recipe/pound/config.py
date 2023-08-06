# -*- coding: utf-8 -*-
# Copyright (C)2008 'ingeniweb'

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
"""Config Recipe pound"""

import os
import zc
from types import BooleanType
from Cheetah.Template import Template

from plone.recipe.pound import utils

RECIPE_BUILD_NAME = 'plone.recipe.pound:build'


def get_options_from_build(buildout, options):
    part = options.get('poundbuildpart', None)
    if part:
        return buildout[part]

    for part in buildout.keys():
        if buildout[part].has_key('recipe') and \
            buildout[part]['recipe'] == RECIPE_BUILD_NAME:
            return buildout[part]
    return {}


class ConfigureRecipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        location = options.get(
            'location', buildout['buildout']['parts-directory'])
        options['location'] = os.path.join(location, name)
        options['prefix'] = options['location']

        self.options = options
        self.buildoptions = get_options_from_build(buildout, options)
        self.options['socket'] = self.buildoptions.get(
            'socket',
            os.path.join(
                self.buildout['buildout']['directory'],
                'var',
                'pound.sock'
            )
        )

    def install(self):
        """ install config fo pound """

        # configures pound
        # loading templates
        curdir = os.path.dirname(__file__)
        tpl = Template(open(os.path.join(curdir, 'pound.cfg.tpl')).read())
        try:
            tpl.daemon = int(self.options.get('daemon',1))
        except ValueError:
            raise zc.buildout.UserError("Deamon is invalid")
        tpl.log_facility = self.options.get('log_facility','daemon')
        try:
            tpl.log_level = int(self.options.get('log_level',1))
        except ValueError:
            raise zc.buildout.UserError("LogLevel is invalid")
        try:
            tpl.alive = int(self.options.get('alive',30))
        except ValueError:
            raise zc.buildout.UserError("Alive is invalid")
        try:
            tpl.dynscale = int(self.options.get('dynscale',0))
        except ValueError:
            raise zc.buildout.UserError("Dynscale is invalid")

        try:
            tpl.client = int(self.options.get('client',10))
        except ValueError:
            raise zc.buildout.UserError("Client is invalid")
        try:
            tpl.timeout = int(self.options.get('timeout',15))
        except ValueError:
            raise zc.buildout.UserError("Timeout is invalid")

        try:
            tpl.grace = int(self.options.get('grace',30))
        except ValueError:
            raise zc.buildout.UserError("Grace is invalid")
        try:
            tpl.owner = self.buildoptions.get('owner', utils.get_sysuser())
        except ValueError:
            raise zc.buildout.UserError("Owner is invalid")
        try:
            tpl.group = self.buildoptions.get('group', utils.get_sysgroup())
        except ValueError:
            raise zc.buildout.UserError("Group is invalid")
        ## session management
        try:
            tpl.sticky = self.options.get('sticky', 'on')
        except ValueError:
            raise zc.buildout.UserError("Sticky is invalid")
        try:
            tpl.sessiontype = self.options.get('sessiontype', 'COOKIE')
        except ValueError:
            raise zc.buildout.UserError("Sessiontype is invalid")
        try:
            tpl.sessiontimeout = int(self.options.get('sessiontimeout', 300))
        except ValueError:
            raise zc.buildout.UserError("SessionTimeout is invalid")
        try:
            tpl.sessioncookie = self.options.get('sessioncookie', '__ac')
        except ValueError:
            raise zc.buildout.UserError("Sessioncookie is invalid")
        try:
            tpl.sessiontimeout = int(self.options.get('sessiontimeout', 300))
        except ValueError:
            raise zc.buildout.UserError("SessionTimeout is invalid")

        tpl.socket = self.options.get('socket', '')

        # creating balancers
        balancer_cfg = []

        for balancer in self.options.get('balancers', '').split('\n'):

            balancer = balancer.strip()
            if balancer == '':
                continue
            balancer = balancer.split()
            name = balancer[0]
            try:
                (adress, port) = balancer[1].split(':')
            except ValueError:
                raise zc.buildout.UserError("balancer syntax is not correct %s" \
                                            % balancer)

            backends = balancer[2:]
            backends_cfg = []

            for backend in backends:
                backend = backend.split(':')
                host = backend[0]
                port_backend = backend[1]
                priority = 0
                timeout = 0
                if ',' in port_backend:
                    l =  port_backend.split(',')
                    if len(l) == 3:
                        (port_backend, priority, timeout) = l

                    elif len(l) == 2:
                        (port_backend, priority) = l
                    else:
                        raise zc.buildout.UserError("Backend configuration is invalid")
                backends_cfg.append({'host': host,
                                    'port': port_backend,
                                    'priority' : priority,
                                    'timeout': timeout})

            balancer_dict = {'name': name,
                             'port': port,
                             'adress': adress,
                             'backends': backends_cfg}

            balancer_cfg.append(balancer_dict)
        tpl.balancers = balancer_cfg


        # writing the file
        if not  os.path.exists(self.options['location']):
            os.mkdir(self.options['location'])
        etc_dir = os.path.join(self.options['location'], 'etc')
        if not os.path.exists(etc_dir):
            os.mkdir(etc_dir)
        var_dir = os.path.join(self.options['location'], 'var')
        if not os.path.exists(var_dir):
            os.mkdir(var_dir)

        filename = os.path.join(etc_dir, 'pound.cfg')
        f = open(filename, 'w')

        try:
            print >>f, tpl
        finally:
            f.close()

        if self.buildoptions:
            self.options['executable'] = os.path.join(self.buildoptions['location'],
                                                      'sbin','pound')
        else:
            if not self.options.get('executable'):
                raise zc.buildout.UserError("path to executable is required")


        pid = os.path.join(var_dir, 'pound.pid')
        scripts = []
        for x in ('poundctl', 'poundrun', 'poundcontrol'):
            ctl = Template(open(os.path.join(curdir, x+'.tpl')).read())
            ctl.poundbin = self.options['executable']
            ctl.socket = self.options.get('socket', '')
            ctl.poundcontrol = os.path.join(
                os.path.dirname(self.options['executable']),
                'poundctl'
            )
            ctl.poundcfg = filename
            ctl.poundpid = pid
            bin_dir = self.buildout['buildout']['bin-directory']
            script_name = os.path.join(bin_dir, self.options.get('%s-binary' % x, x))
            f = open(script_name, 'w')
            try:
                print >>f, ctl
            finally:
                f.close()
            os.chmod(script_name, 0755)
            scripts.append(script_name)

        return [etc_dir] + scripts
