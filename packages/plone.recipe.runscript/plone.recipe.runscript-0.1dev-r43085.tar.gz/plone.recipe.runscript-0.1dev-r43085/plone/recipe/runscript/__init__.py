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
__revision__ = "$Revision: 43085 $"

import os
import subprocess

class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout, self.options, self.name = buildout, options, name

        options['location'] = os.path.join(
            buildout['buildout']['bin-directory'],
            self.name,
            )
        options['script'] = "%(location)s.py" % options
        options['bin-directory'] = buildout['buildout']['bin-directory']
        options['scripts'] = '' # suppress script generation.
        options["args"] = options.get( "args", "" )

        instance_home = options["instance-home"]
        options['instance-script'] = os.path.basename( instance_home )

    def install(self):
        options = self.options
        location = options['location']

        cmd = "%(bin-directory)s/%(instance-script)s run %(script)s %(args)s" % options
        subprocess.call( cmd.split() )
        return location

    def update(self):
        pass

# vim: set ft=python ts=4 sw=4 expandtab :
