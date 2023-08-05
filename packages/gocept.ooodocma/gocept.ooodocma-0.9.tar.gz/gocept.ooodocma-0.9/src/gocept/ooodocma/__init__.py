##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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

import os.path

import zc.recipe.egg

import gocept.download


class Recipe:
    """Downloads and configures a docmaserver/openoffice frankenstein

    Parameters:

        ip - ip for the docmaserver to listen on
        port - port for the docmaserver to listen on
        password - password for the docmaserver

        url - url to the docmaserver frankenstein package
        md5sum - md5sum for verification

        storage - directory to store jobs in
        smtpserver - hostname or ip of smtpserver to use
        email - sender email address for job notifications

    """

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name
        self.package_download = gocept.download.Recipe(buildout, name, options)

        options['scripts'] = ''
        options['eggs'] = ''
        options.pop('entry-points', None)
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

    def install(self):
        paths = self.package_download.install()

        if not os.path.isdir(self.options['storage']):
            # Fails if the storage path is a file.
            os.mkdir(self.options['storage'])

        for config_file in [('docmaserver', 'docma_config.cfg'),
                            ('docmaserver', 'zdaemon.conf'),
                            ('oood', 'oood-config.xml'),
                            ('oood', 'zdaemon.conf')]:
            self._update_config_file(os.path.join(*config_file))

        # start scripts
        requirements, ws = self.egg.working_set(('zdaemon',))
        oood_script_name = self.name+'-oood'
        zc.buildout.easy_install.scripts(
            [(oood_script_name, 'zdaemon.zdctl', 'main')],
            ws, self.options['executable'], self.options['bin-directory'],
            arguments = ('\n        ["-C", %r]'
                         '\n        + sys.argv[1:]'
                         % os.path.join(self.options['location'], 'oood', 'zdaemon.conf')
                         )
            )
        docma_script_name = self.name+'-docma'
        zc.buildout.easy_install.scripts(
            [(docma_script_name, 'zdaemon.zdctl', 'main')],
            ws, self.options['executable'], self.options['bin-directory'],
            arguments = ('\n        ["-C", %r]'
                         '\n        + sys.argv[1:]'
                         % os.path.join(self.options['location'], 'docmaserver', 'zdaemon.conf')
                         )
            )

        paths.append(os.path.join(self.options['bin-directory'], oood_script_name))
        paths.append(os.path.join(self.options['bin-directory'], docma_script_name))
        return paths

    def update(self):
        pass

    def _update_config_file(self, filename):
        filename = os.path.join(self.options['location'], filename)
        data = open(filename+'.in').read()
        data = data % self.options
        new = open(filename, 'w')
        new.write(data)
        new.close()
