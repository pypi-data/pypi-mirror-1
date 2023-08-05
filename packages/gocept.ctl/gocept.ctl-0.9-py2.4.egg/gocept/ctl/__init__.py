##############################################################################
#
# Copyright (c) 2007 gocept gmbh & co. kg and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os
import urlparse
import urllib
import md5
import tempfile
import subprocess
import shutil

script_template = """#!/bin/sh

start ()
{
    echo 'Starting ...'
%(start)s
}

stop ()
{
    echo 'Stopping ...'
%(stop)s

}

help ()
{
    echo "Usage: $0 <start|stop|restart>"
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        start
        stop
        ;;
    *)
        help
        ;;
esac
"""


class Recipe:
    """Recipe that creates a shell script to start/stop multiple services
    in a buildout.

    Configuration options:

        scripts ... list of script names to control (priority by order)

    """

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name
        self.base = self.buildout['buildout']['bin-directory']
        self.scripts = self.options['scripts'].split()

    def update(self):
        # No update needed, only run when configuration changes
        pass

    def install(self):
        script = script_template % {'start': self._generate_commands('start'),
                                    'stop': self._generate_commands('stop', reverse=True)}
        script_name = os.path.join(self.base, self.name)
        f = open(script_name, 'wb')
        f.write(script)
        f.close()
        os.chmod(script_name, 0755)
        return script_name

    def _generate_commands(self, command, reverse=False):
        """Build the list of commands for all scripts."""
        commands = ""
        scripts = self.scripts
        if reverse:
            scripts = reversed(self.scripts)
        for script in scripts:
            commands += "\techo %s ...\n" % script
            commands += ("\t%s %s\n" %
                         (os.path.join(self.base, script), command))
        return commands
