# -*- coding: utf-8 -*-
#
# File: __init__.py
#
# Copyright (c) InQuant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__author__ = """Stefan Eletzhofer <stefan.eletzhofer@inquant.de>"""
__docformat__ = 'plaintext'
__revision__ = "$Revision: 61468 $"

import os
import sys
import subprocess

class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout, self.options, self.name = buildout, options, name

        options['location'] = os.path.join(
            buildout['buildout']['bin-directory'],
            self.name,
            )
        options['script'] = self.options.get('script',
                                "%(location)s.py" % options)
        options['bin-directory'] = buildout['buildout']['bin-directory']
        options['scripts'] = '' # suppress script generation.
        options["args"] = options.get( "args", "" )
        is_win = sys.platform[:3].lower() == "win"
        instance_home = options["instance-home"]
        instance_script = os.path.basename(instance_home)
        if is_win:
            instance_script = "%s.exe" % instance_script
        options['instance-script'] = instance_script
        self.zeo_home = options.get('zeo-home', False)
        if self.zeo_home:
            if is_win:
                zeo_script = 'zeoservice.exe'
            else:
                zeo_script = os.path.basename(self.zeo_home)
            options['zeo-script'] = zeo_script

    def install(self):
        options = self.options
        location = options['location']
        # start the zeo if it exists
        if self.zeo_home:
            zeo_cmd = "%(bin-directory)s/%(zeo-script)s" % options
            zeo_start = "%s start" % zeo_cmd
            subprocess.call(zeo_start.split())
        # run the script
        cmd = "%(bin-directory)s/%(instance-script)s run %(script)s %(args)s" % options
        subprocess.call( cmd.split() )
        # stop the zeo
        if self.zeo_home:
            zeo_stop = "%s stop" % zeo_cmd
            subprocess.call(zeo_stop.split())
        return location

    def update(self):
        pass

# vim: set ft=python ts=4 sw=4 expandtab :
