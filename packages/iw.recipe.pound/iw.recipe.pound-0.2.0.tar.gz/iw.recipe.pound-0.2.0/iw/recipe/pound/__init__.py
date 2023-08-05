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
"""Recipe pound"""
import os

from zc.recipe.cmmi import Recipe as CMMIRecipe

TEMPLATE = """\
#!/bin/sh

%(pound)s -f %(cfg)s -p %(pid)s 

"""

class Recipe(CMMIRecipe):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        CMMIRecipe.__init__(self, buildout, name, options)
        self.buildout = buildout

    def install(self):
        """installer"""
        # building extra options
        owner = self.options.get('owner', 'www-data')
        group = self.options.get('group', owner)

        extra = '--with-owner=%s --with-group=%s' % (owner, group)
        self.options['extra_options'] = extra

        # uses cmmi installer
        installed = CMMIRecipe.install(self)

        # configures pound
        # loading templates
        curdir = os.path.dirname(__file__)
        main_tp = open(os.path.join(curdir, 'pound.cfg_tmpl')).read()
        balancer_tp = open(os.path.join(curdir, 'pound_balancer.cfg_tmpl')).read()
        backend_tp = open(os.path.join(curdir, 'pound_backend.cfg_tmpl')).read()

        # creating balancers
        balancer_cfg = []

        for balancer in self.options.get('balancers', '').split('\n'):
            balancer = balancer.strip()
            if balancer == '':
                continue
            balancer = balancer.split()
            name = balancer[0]
            port = balancer[1]
            backends = balancer[2:]
            backends_cfg = []

            for backend in backends:
                backend = backend.split(':')
                host = backend[0]
                port_backend = backend[1]
                backends_cfg.append(backend_tp % {'host': host,
                                                  'port': port_backend})

            backends_cfg = ''.join(backends_cfg)
            balancer_dict = {'name': name,
                             'port': port,
                             'backends': backends_cfg}

            balancer_cfg.append(balancer_tp % balancer_dict)

        balancers = ''.join(balancer_cfg)
        self.options['balancers'] = balancers
        conf = main_tp % self.options

        # writing the file
        etc_dir = os.path.join(self.options['location'], 'etc')
        if not os.path.exists(etc_dir):
            os.mkdir(etc_dir)
        var_dir = os.path.join(self.options['location'], 'var')
        if not os.path.exists(var_dir):
            os.mkdir(var_dir)

        filename = os.path.join(etc_dir, 'pound.cfg')
        f = open(filename, 'w')
        try:
            f.write(conf)
        finally:
            f.close()

        # building the script that launches pound
        command = os.path.join(self.options['location'], 'sbin', 'pound')
        pid = os.path.join(var_dir, 'pound.pid')
        
        script = TEMPLATE % {'pound': command, 'cfg': filename, 
                             'pid': pid}

        bin_dir = self.buildout['buildout']['bin-directory']
        script_name = os.path.join(bin_dir, self.name)
        f = open(script_name, 'wb')
        f.write(script)
        f.close()
        os.chmod(script_name, 0755)
        return (installed, filename, script_name)

    def update(self):
        """updater"""
        pass

