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

import gocept.download


# This function was taken from zc.recipe.cmmi:
def system(command):
    if os.system(command):
        raise SystemError("Failed", command)


class Recipe(object):
    """zc.buildout recipe for building a software package from source.

    Configuration options:

        extra-options

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

        # The extra options treatment was taken from zc.recipe.cmmi:
        extra_options = self.options.get('extra-options', '')
        # get rid of any newlines that may be in the options so they
        # do not get passed through to the commandline
        extra_options = ' '.join(extra_options.split())

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

        here = os.getcwd()
        os.chdir(build_dir)
        try:
            system("./configure --prefix=%s %s" % (location, extra_options))
            system("make")
            system("make install")
        finally:
            os.chdir(here)

        shutil.rmtree(build_dir)
        return [location,
                ]

    def update(self):
        pass
