# -*- coding: utf-8 -*-
#
# Copyright (c) InQuant GmbH
#
# This Program may be used by anyone in accordance with the terms of the 
# LGPL

__author__ = """Stefan Eletzhofer <stefan.eletzhofer@inquant.de>"""
__docformat__ = 'plaintext'
__revision__ = "$Revision: 1970 $"

import os
import logging

logger = logging.getLogger("inquant.recipe.vimproject")

info = logger.info
warning = logger.warning
error = logger.info

def create_project_file(patterns):
    from inquant.tools.mkvimproject import run
    dir = os.path.basename(os.getcwd())
    filename=os.path.join(os.getcwd(), "%s.vpj" % dir )
    info("Creating project file '%s'" % filename )
    run( dir, file(filename, "w"), patterns)
    return filename

class Recipe(object):
    """
    A Recipe which creates a VIM Projectfile.

    Parameters:

    patterns     ... a list of file extensions to list inside the project,
                     e.g. something like ".py .zcml .pt .xml"
                     default: ${buildout:template-directory}/$(name)s.in
                     OPTIONAL
    tags         ... tags to add

    Available keys:

    location     ... the filename of the created project file
    """

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name

        if not options.get('patterns'):
            options['patterns'] = ""

        if not options.get('tags'):
            options['tags'] = ""


    def install(self):
        options = self.options

        # create project file
        location = create_project_file(options["patterns"])
        self.options["location"] = location

        # create IN.vim (tags)
        invim = file("in.vim", "w")
        print >>invim, "set tags=", os.path.join(os.getcwd(), "tags"), options["tags"]
        invim.close()

        return location


    update = install

# vim: set ft=python ts=4 sw=4 expandtab :

