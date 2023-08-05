#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-msg=C0301,W0613,W0612,C0103


"""

cli.py
======

Command-line code for g-pypi


"""

import sys
import optparse
import logging

from pkg_resources import Requirement
from portage import portage_exception

from yolk.pypi import CheeseShop
from yolk.yolklib import get_highest_version
from yolk.setuptools_support import get_download_uri
from g_pypi.ebuild import Ebuild


__docformat__ = 'restructuredtext'


def url_from_pypi(package_name, version):
    """Query PyPI for package's download URL"""
    pypi = CheeseShop()

    try:
        return pypi.get_download_urls(package_name, version, pkg_type="source")[0]
    except IndexError:
        return None

def get_uri(package_name, version):
    """Attempt to find a package's download URI"""
    #LOGGER.debug("Querying PyPI for download URI...")
    download_url = url_from_pypi(package_name, version)

    if not download_url:
        #Sometimes setuptools can find a package URI if PyPI doesn't have it
        download_url = uri_from_setuptools(package_name, version)

    if not download_url:
        LOGGER.error("Can't find SRC_URI for '%s'." %  package_name)
        sys.exit(2)

    LOGGER.debug("Package URI: %s " % download_url)
    return download_url

def uri_from_setuptools(package_name, version):
    """Use setuptools to find a package's URI"""
    #LOGGER.debug("Using setuptools to find package URI...")
    try:
        req = Requirement.parse(package_name)
    except ValueError:
        print >> sys.stderr, "The package seems to have a ridiculous name or version, can't proceed."
        sys.exit(2)

    #First check for source
    src_uri = get_download_uri("source", package_name, version)
    if not src_uri:
        src_uri = get_download_uri("binary", package_name, version)
        if src_uri:
            LOGGER.error("The package has no source URI available (binary only).")
            LOGGER.error(src_uri[0])
        else:
            LOGGER.error("The package has no source URI available.")
        sys.exit(2)
    return src_uri[0]

def do_ebuild(package_name, version, options):
    """Download package using PyPI and attempt to create ebuild"""
    if options.pv:
        force_pv = options.pv
    else:
        force_pv = ""
    if options.pn:
        force_pn = options.pn
    else:
        force_pn = ""
    #Test project name and get proper case for project name:
    #LOGGER.debug("Querying PyPI to verify package name...")
    pypi = CheeseShop()
    (package_name, versions) = pypi.query_versions_pypi(package_name, False)

    #Unfortunately PyPI shows 'hidden' package versions as non-existant.
    #This shouldn't happen with the XML-RPC interface, I'd think.
    #Bug upstream (Cheese Shop) to fix?
    if version and version not in versions:
        LOGGER.error("Can't find package for version:'%s'." %  version)
        return 2

    download_url = get_uri(package_name, version)

    if options.pn:
        pn = options.pn
    else:
        pn = package_name.lower()
    if options.pv:
        pv = options.pv
    else:
        #Use highest version returned from PyPI
        pv = versions[0]

    ebuild = Ebuild(pn, pv, options, LOGGER)
    #Determine SRC_URI, MY_P, MY_PN, MY_P
    try:
        ebuild.get_ebuild_vars(download_url, force_pn, force_pv)
    except portage_exception.InvalidVersionString:
        LOGGER.error("Can't determine PV, use -v to set it: %s-%s" % (pn, pv))
        return 2
    except portage_exception.InvalidPackageName:
        LOGGER.error("Can't determine PN, use -n to set it: %s-%s" % (pn, pv))
        return 2

    ebuild.set_metadata(query_metadata(package_name, version))

    ebuild.make_ebuild_file()
    if options.category:
        ebuild.category = options.category
    else:
        ebuild.category = "dev-python"

    if options.pretend:
        print "%s/%s-%s" % (ebuild.category, ebuild.vars['pn'],
                ebuild.vars['pv'])
        print
        print ebuild.ebuild_text
        ebuild.show_warnings()
        return

    ebuild.create_ebuild()
    LOGGER.debug(ebuild.ebuild_text)

def query_metadata(package_name, version):
    """Get package metadata from PyPI"""
    pypi = CheeseShop()
    if version:
        return pypi.release_data(package_name, version)
    else:
        (pn, vers) = pypi.query_versions_pypi(package_name)
        return pypi.release_data(package_name, get_highest_version(vers))

def parse_pkg_ver(package_spec):
    """Return tuple with package_name and version from CLI args"""

    arg_str = ("").join(package_spec)
    if "==" not in arg_str:
        #No version specified
        package_name = arg_str
        version = None
    else:
        (package_name, version) = arg_str.split("==")
        package_name = package_name.strip()
        version = version.strip()
    return (package_name, version)


def main():
    """Parse command-line options and do it."""

    usage = "usage: %prog [options] <package_name[==version]>"
    opt_parser = optparse.OptionParser(usage=usage)

    opt_parser.add_option("-p", "--pretend", action='store_true', dest=
                         "pretend", default=False, help=
                         "Print ebuild to stdout, don't write ebuild file, \
                         don't download SRC_URI.")

    opt_parser.add_option("-o", "--overwrite", action='store_true', dest=
                         "overwrite", default=False, help=
                         "Overwrite existing ebuild.")

    opt_parser.add_option("-c", "--portage-category", action='store', dest=
                         "category", default=False, help=
                         "Specify PN to use when naming ebuild.")

    opt_parser.add_option("-n", "--PN", action='store', dest=
                         "pn", default=False, help=
                         "Specify PN to use when naming ebuild.")

    opt_parser.add_option("-v", "--PV", action='store', dest=
                         "pv", default=False, help=
                         "Specify PV to use when naming ebuild.")

    opt_parser.add_option("--MY_PV", action='store', dest=
                         "my_pv", default=False, help=
                         "Specify MY_PV")

    opt_parser.add_option("--MY_PN", action='store', dest=
                         "my_pn", default=False, help=
                         "Specify MY_PN")

    opt_parser.add_option("--MY_P", action='store', dest=
                         "my_p", default=False, help=
                         "Specify MY_P")

    opt_parser.add_option("-V", "--verbose", action='store_true', dest=
                         "verbose", default=False, help=
                         "Show more output.")

    (options, package_spec) = opt_parser.parse_args()
    if options.verbose:
        LOGGER.setLevel(logging.DEBUG)
    else:
        LOGGER.setLevel(logging.INFO)
    if not package_spec:
        opt_parser.print_help()
        LOGGER.error("\nError: You need to specify a package name at least.")
        return 2
    (package_name, version) = parse_pkg_ver(package_spec)
    
    return do_ebuild(package_name, version, options)

LOGGER = logging.getLogger("g-pypi")
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.StreamHandler())

if __name__ == "__main__":
    sys.exit(main())

