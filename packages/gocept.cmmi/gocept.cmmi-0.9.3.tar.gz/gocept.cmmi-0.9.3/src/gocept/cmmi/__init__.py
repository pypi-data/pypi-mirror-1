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
import os.path
import tempfile
import shutil
import subprocess

import gocept.download


class Recipe(object):
    """zc.buildout recipe for building a software package from source.

    Configuration options:

        make: The name of the make executable, defaults to "make".

        extra-options: A string appended to the configure command line.

        extra-vars: Additional environment variables for the cmmi process,
                    specified as name=value pairs, each on its own line.
                    Values may be double-quoted to protect whitespace.
                    Variables with empty values are removed entirely.

    Options passed to gocept.download:

        url
        strip-top-level-dir
        md5sum

    The temporary build_dir will be removed after the part is successfully
    installed or if the download fails. It will be kept for debugging if the
    configure/make/make install process itself fails.

    """

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )

    def install(self):
        build_dir = tempfile.mkdtemp("buildout-" + self.name)

        make = self.options.get("make", "make")
        extra_options = self.options.get('extra-options', '')
        environ = os.environ.copy()
        update_environ(environ, self.options.get("extra-vars", ""))

        try:
            dl_options = self.options.copy()
            dl_options["destination"] = build_dir
            gocept.download.Recipe(self.buildout, self.name, dl_options
                                   ).install()
        except:
            shutil.rmtree(build_dir)
            raise

        location = self.options["location"]
        if not os.path.exists(location):
            os.mkdir(location)
        else:
            assert os.path.isdir(location)

        self._create_structure()

        here = os.getcwd()
        os.chdir(build_dir)
        install_target = self.options.get('install-target', 'install')
        try:
            call("./configure --prefix=%s %s" % (location, extra_options),
                 environ, shell=True)
            call([make], environ)
            call([make, install_target], environ)
        finally:
            os.chdir(here)

        shutil.rmtree(build_dir)
        return [location,
                ]

    def update(self):
        pass

    def _create_structure(self):
        location = self.options['location']
        precreate = self.options.get('create-directories', '').split()
        for name in precreate:
            path = os.path.join(location, name)
            if os.path.exists(path):
                continue
            os.makedirs(path)


def update_environ(environ, extra_vars):
    for line in extra_vars.splitlines():
        if line.strip():
            name, value = line.split('=', 1)
            name, value = name.strip(), value.strip()
            if value[0] == value[-1] == '"':
                value = value[1:-1]
            if value:
                environ[name] = value
            elif name in environ:
                del environ[name]


def call(command, environ, **kwargs):
    if subprocess.call(command, env=environ, **kwargs):
        raise SystemError("Failed", command)
