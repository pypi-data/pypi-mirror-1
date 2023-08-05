#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-msg=C0301,W0613,W0612,C0103

"""

portage_utils
=============

Various functions dealing with portage

"""


import sys
import os
import commands

import portage



__docformat__ = 'restructuredtext'

ENV = portage.config(clone=portage.settings).environ()

def unpack_ebuild(ebuild_path):
    """Use portage to unpack an ebuild"""
    (status, output) = commands.getstatusoutput("ebuild %s clean digest setup clean unpack" % ebuild_path)
    if status:
        #Portage's error message, sometimes.
        #err_msg = output.split()[0]
        #Couldn't determine PN or PV so we misnamed ebuild
        if 'does not follow correct package syntax' in output:
            print >> sys.stderr, output
            print >> sys.stderr, "Misnamed ebuild: ", ebuild_path
            print >> sys.stderr, "Try using -n or -v to force PN or PV"
            os.unlink(ebuild_path)
        else:
            print >> sys.stderr, output
        sys.exit(status)
  
def find_s_dir(p, cat):
    """Try to get S by determining what directories were unpacked"""
    workdir = get_workdir(p, cat)
    files = os.listdir(workdir)
    dirs = []
    for unpacked in files:
        if os.path.isdir(os.path.join(workdir, unpacked)):
            dirs.append(unpacked)
    if len(dirs) == 1:
        #Only one directory, must be it.
        return dirs[0]
    else:
        print >> sys.stderr, "Unpacked multiple directories - can't determine ${S}", dirs
 
def get_workdir(p, cat):
    """Return WORKDIR"""
    return '%s/portage/%s/%s/work' % (get_portage_tmpdir(), cat, p)

def get_portdir_overlay():
    """Return PORTDIR_OVERLAY from /etc/make.conf"""
    return ENV['PORTDIR_OVERLAY'].split(" ")[0]

def get_portage_tmpdir():
    """Return PORTAGE_TMPDIR from /etc/make.conf"""
    return ENV["PORTAGE_TMPDIR"]

def get_portdir():
    """Return PORTDIR from /etc/make.conf"""
    return ENV["PORTDIR"]
    
def get_keyword():
    """Return first ACCEPT_KEYWORDS from /etc/make.conf"""
    #Choose the first arch they have, in case of multiples.
    arch = ENV["ACCEPT_KEYWORDS"].split(' ')[0]
    #New ebuilds must be in the testing branch
    if not arch.startswith('~'):
        arch = "~%s" % arch
    return arch

def make_overlay_dir(category, pn, overlay):
    """Create directory(s) in overlay for ebuild"""
    ebuild_dir = os.path.join(overlay, category, pn)
    if not os.path.isdir(ebuild_dir):
        os.makedirs(ebuild_dir)
    return ebuild_dir

