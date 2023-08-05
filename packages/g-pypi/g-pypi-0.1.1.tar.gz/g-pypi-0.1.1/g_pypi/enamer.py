#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103

"""
enamer.py
=========

Functions for extracting useful info from a pkg URI
such as PN, PV, MY_P, SRC_URI

* Examples:

    http://www.foo.com/pkgfoo-1.0.tbz2
    PN="pkgfoo"
    PV="1.0"
    Ebuild name: pkgfoo-1.0.ebuild
    SRC_URI="http://www.foo.com/${P}.tbz2"

    http://www.foo.com/PkgFoo-1.0.tbz2
    PN="pkgfoo"
    PV="1.0"
    Ebuild name: pkgfoo-1.0.ebuild
    MY_P="PkgFoo-${PV}"
    SRC_URI="http://www.foo.com/${MY_P}.tbz2"

    http://www.foo.com/pkgfoo_1.0.tbz2
    PN="pkgfoo"
    PV="1.0"
    Ebuild name: pkgfoo-1.0.ebuild
    MY_P="${PN}_${PV}"
    SRC_URI="http://www.foo.com/${MY_P}.tbz2"

    http://www.foo.com/PKGFOO_1.0.tbz2
    PN="pkgfoo"
    PV="1.0"
    Ebuild name: pkgfoo-1.0.ebuild
    MY_P="PKGFOO_${PV}"
    SRC_URI="http://www.foo.com/${MY_P}.tbz2"

    http://www.foo.com/pkg-foo-1.0_beta1.tbz2
    PN="pkg-foo"
    PV="1.0_beta1"
    Ebuild name: pkg-foo-1.0_beta1.ebuild
    SRC_URI="http://www.foo.com/${P}.tbz2"

"""

import urlparse

from portage import pkgsplit, portage_dep, portage_exception

__docformat__ = 'restructuredtext'


def get_filename(uri):
    """return file name minus extension from src_uri"""
    path = urlparse.urlparse(uri)[2]
    path = path.split('/')
    return strip_ext(path[len(path)-1])

def strip_ext(fname):
    """Strip possible extensions from filename."""
    valid_extensions = [".zip", ".tgz", ".tar.gz", ".tar.bz2", ".tbz2"]
    for ext in valid_extensions:
        if fname.endswith(ext):
            fname = fname.replace(ext, "")
            break
    return fname

def is_valid_uri(uri):
    """Check if URI's addressing scheme is valid"""
    if uri.startswith("http:") or uri.startswith("ftp:") or \
            uri.startswith("mirror:"):
        return True

def parse_sourceforge_uri(uri):
    """Change URI to mirror://sourceforge format"""
    uri_out = homepage = ""
    if uri.find('sourceforge') != -1:
        tst_uri = urlparse.urlparse(uri)
        if tst_uri[2].find('sourceforge') != -1:
            uri_out = 'mirror:/%s' % tst_uri[2]
            homepage = "http://sourceforge.net/projects/%s/" % \
                       tst_uri[2].split("/")[2]
    return uri_out, homepage

def is_good_filename(uri):
    """If filename is sane enough to deduce PN & PV, return pkgsplit results"""
    if is_valid_uri(uri):
        psplit = split_p(uri)
        if psplit and psplit[0].islower():
            return psplit

def split_p(uri):
    """Try to split a URI into PN, PV"""
    p = get_filename(uri)
    psplit = pkgsplit(p)
    return psplit

def get_components(uri):
    """Split uri into pn and pv and new uri"""
    p = get_filename(uri)
    psplit = split_p(uri)
    uri_out = uri.replace(p, "${P}") 
    pn = psplit[0].lower()
    pv = psplit[1]
    return uri_out, pn, pv

def get_myp(uri):
    """Return MY_P and new uri with MY_P in it"""
    my_p = get_filename(uri)
    uri_out = uri.replace(my_p, "${MY_P}") 
    return uri_out, my_p

def guess_components(my_p):
    """Try to break up raw MY_P into PN and PV"""
    pn, pv = "", ""

    # Ok, we just have one automagical test here.
    # We should look at versionator.eclass for inspiration
    # and then come up with several functions.
    my_p = my_p.replace("_", "-")

    psplit = pkgsplit(my_p)
    if psplit:
        pn = psplit[0].lower()
        pv = psplit[1]
    return pn, pv

def get_vars(uri, up_pn, up_pv, pn="", pv=""):
    """Determine MY_ variables from URI"""
    if pv:
        force_pv = pv
    else:
        force_pv = ""

    my_pn = my_pv = ""

    #No PN or PV given on command-line, try upstream's name/version
    if not pn and not pv:
        if pn:
            pv = up_pv
        elif pv:
            my_pn = pn
            pn = up_pn.lower()
        else:
            parts = split_p(uri)
            if parts:
                # pylint: disable-msg=W0612
                # unused variable 'rev'
                # The 'rev' is never used because these are
                # new ebuilds being created.
                pn, pv, rev = parts
            else:
                pn = up_pn
                pv = up_pv

    if pn and not pv:
        pv = up_pv
    elif pv and not pn:
        pn = up_pn

    if not pn.islower():
        my_pn = pn
        pn = pn.lower()
    p = "%s-%s" % (pn, pv)
    src_uri, my_p, my_p_raw = get_src_uri(uri)
    if force_pv:
        pv = force_pv

    if not portage_dep.isvalidatom("=dev-python/%s-%s" % (pn, pv)):
        if not portage_dep.isjustname("dev-python/%s-%s" % (pn, pv)):
            raise portage_exception.InvalidPackageName(pn)
        else:
            raise portage_exception.InvalidVersionString(pv)
    #some-pkg-1.0 -> some-pkg
    my_pn = "-".join(my_p.split("-")[:-1])
    if my_pn == pn:
        my_pn = ""
    if my_p == my_pn + "-${PV}":
        my_p = "${MY_PN}-${PV}"
    parts = {'pn': pn,
            'pv': pv,
            'p': p,
            'my_p': my_p,
            'my_pn': my_pn,
            'my_pv': my_pv,
            'my_p_raw': my_p_raw,
            'src_uri': src_uri,
            }
    return parts

def get_src_uri(uri):
    """Return src_uri"""
    my_p = my_p_raw = ''
    if is_good_filename(uri):
        src_uri, pn, pv = get_components(uri)
    else:
        src_uri, my_p = get_myp(uri)
        pn, pv = guess_components(my_p)
        if pn and pv:
            my_p_raw = my_p
            my_p = my_p.replace(pn, "${PN}")
            my_p = my_p.replace(pv, "${PV}")

    return src_uri, my_p, my_p_raw

