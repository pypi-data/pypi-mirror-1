# -*- coding: utf-8 -*-
#
# Copyright (c) InQuant GmbH
#
# This Program may be used by anyone in accordance with the terms of the 
# LGPL

__author__ = """Stefan Eletzhofer <stefan.eletzhofer@inquant.de>"""
__docformat__ = 'plaintext'
__revision__ = "$Revision: 59016 $"

import os
import logging

logger = logging.getLogger("inquant.recipe.vimproject")

info = logger.info
warning = logger.warning
error = logger.info

def create_project_file(patterns):
    from inquant.tools.mkvimproject import mkvimproject
    dir = os.getcwd()
    basename = os.path.basename(os.getcwd())
    path=os.path.join(dir, "%s.vpj" % basename )
    info("Creating project file '%s'" % path )
    mkvimproject.run( dir, file(path, "w"), patterns)
    return path

class Recipe(object):
    """
    A Recipe which creates a VIM Projectfile.

    Parameters:

    patterns     ... a list of file extensions to list inside the project,
                     e.g. something like ".py .zcml .pt .xml"
                     default: ${buildout:template-directory}/$(name)s.in
                     OPTIONAL
    tags         ... tags to add
    create_tagfile ... create tag file if key is present
    in_vim_additional ... additional stuff to put in in.vim verbatim.

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
        out = []
        options = self.options

        # create project file
        location = create_project_file(options["patterns"])
        self.options["location"] = location
        out.append(location)

        # update tags
        if "create_tagfile" in options.keys():
            import subprocess
            info("creating tag file ...")
            subprocess.call("ctags -R .".split())
            out.append("tags")

        # create in.vim (tags)
        info("creating 'in.vim' ...")
        invim = file("in.vim", "w")
        print >>invim, "set tags=%s" % ",".join( [os.path.join(os.getcwd(), "tags"), options["tags"]])
        if "in_vim_additional" in options.keys():
            print >>invim, options.get("in_vim_additional")
        invim.close()
        out.append("in.vim")


        return out


    update = install

# vim: set ft=python ts=4 sw=4 expandtab :

