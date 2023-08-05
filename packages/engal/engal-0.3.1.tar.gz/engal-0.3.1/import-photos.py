#!/usr/bin/env python2.4
import pkg_resources
pkg_resources.require("TurboGears")

import turbogears
import cherrypy
cherrypy.lowercase_api = True

from os.path import *
import sys
import os

# first look on the command line for a desired config file,
# if it's not on the command line, then
# look for setup.py in this directory. If it's not there, this script is
# probably installed
if os.environ.get('ENGAL_PATH'):
    turbogears.update_config(configfile=join(os.environ['ENGAL_PATH'], 'prod.cfg'),
        modulename="engal.config")
if exists(join(dirname(__file__), "setup.py")):
    turbogears.update_config(configfile=join(dirname(__file__), "dev.cfg"),
        modulename="engal.config")
else:
    turbogears.update_config(configfile="prod.cfg",
        modulename="engal.config")

from engal.model import *

import os.path

def imp(dummy, dirname, fnames):
    print "Directory: %s" % (dirname)
    for sfn in fnames:
        if not (sfn.endswith(".jpg") or sfn.endswith(".jpeg")):
            continue
        ignore = False
        for banned in ['.sized.', '.thumb.', '.highlight.']:
            if banned in sfn:
                ignore = True
                break
        if ignore:
            continue
        fn = os.path.join(dirname, sfn)
        if os.path.isfile(fn):
            p = Photo(filename=sfn, name=sfn, description=sfn, owner=user)
            p.contents = file(fn).read()
            photoset.addPhoto(p)

username = sys.argv[1]
photoset_name = sys.argv[2]
directory = sys.argv[3]

user = User.by_user_name(username)
photoset = PhotoSet.select(PhotoSet.q.name == photoset_name)[0]

os.path.walk(directory, imp, None)

