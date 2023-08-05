#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103,C0301,E0611

# Reasons for pylint disable-msg's
# E0611 - No name 'resource_string' in module 'pkg_resources'
# C0103 - Variable names too short (p, pn, pv etc.)
# C0301 - Line too long in some docstrings
"""

ebuild.py
======

Creates an ebuild


"""

import re
import sys
import os
import os.path
from time import localtime

from Cheetah.Template import Template
from pkg_resources import resource_string
from configobj import ConfigObj

from g_pypi.portage_utils import make_overlay_dir, find_s_dir, unpack_ebuild, \
        get_keyword, get_portdir, get_workdir, get_portdir_overlay
from g_pypi import enamer


__docformat__ = 'restructuredtext'

#Cheetah template
EBUILD_TEMPLATE = 'ebuild.tmpl'


class Ebuild:

    """Contains ebuild"""
    
    def __init__(self, pn, pv, options, logger):
        """Setup ebuild variables"""
        #Variables that will be passed to the Cheetah template
        self.options = options
        self.overwrite = options.overwrite
        self.metadata = None
        self.category = ""
        self.ebuild_text = ""
        self.ebuild_path = ""
        self.logger = logger
        self.unpacked_dir = ""
        self.s = ""
        self.depends = []
        self.rdepends = []
        self.use = []
        self.config = self.get_config()
        self.warnings = []
        self.python_modname = ""
        self.vars = {
                'pn': pn,
                'pv': pv,
                'p': "%s-%s" % (pn, pv),
                'keywords': self.config['keyword']
                }

    def get_config(self):
        """Read config file, create if it doesn't exist"""
        rc_file = os.path.expanduser("~/.g-pypirc")
        if not os.path.exists(rc_file):
            self.logger.info("\n ** No config file found - writing one...")
            config = ConfigObj()
            config.filename = rc_file
            config['keyword'] = get_keyword()
            config['overlay'] = get_portdir_overlay()
            config.write()
            self.logger.info("Your default keyword will be: %s " % \
                    config['keyword'])
            self.logger.info("Your default overlay will be: %s " % \
                    config['overlay'])
            self.logger.info("To change these edit: %s \n\n" % rc_file)
        return ConfigObj(rc_file) 

    def set_metadata(self, metadata):
        """Set metadata"""
        if metadata:
            self.metadata = metadata
        else:
            self.logger.error("Package has no metadata.")
            sys.exit(2)

    def get_ebuild_vars(self, download_url, force_pn="", force_pv=""):
        """Determine variables from SRC_URI"""
        if force_pn or force_pv:
            ebuild_vars = enamer.get_vars(download_url, self.vars['pn'], 
                    self.vars['pv'], force_pn, force_pv)
        else:
            ebuild_vars = enamer.get_vars(download_url, self.vars['pn'], 
                    self.vars['pv'])
        if self.options.my_p:
            ebuild_vars['my_p'] = self.options.my_p

        if self.options.my_pv:
            ebuild_vars['my_pv'] = self.options.my_pv

        if self.options.my_pn:
            ebuild_vars['my_pn'] = self.options.my_pn

        if ebuild_vars.has_key('my_p'):
            self.vars['my_p'] = ebuild_vars['my_p']
            self.vars['my_p_raw'] = ebuild_vars['my_p_raw']
        else:
            self.vars['my_p'] = ''
            self.vars['my_p_raw'] = ebuild_vars['my_p_raw']
        if ebuild_vars.has_key('my_pn'):
            self.vars['my_pn'] = ebuild_vars['my_pn']
        else:
            self.vars['my_pn'] = ''
        if ebuild_vars.has_key('my_pv'):
            self.vars['my_pv'] = ebuild_vars['my_pv']
        else:
            self.vars['my_pv'] = ''
        self.vars['src_uri'] = ebuild_vars['src_uri']


    def add_metadata(self):
        """Extract relevant ebuild variables from metadata"""

        #There doesn't seem to be any specification for case
        if self.metadata.has_key('Summary'):
            self.vars['description'] = self.metadata['Summary']
        elif self.metadata.has_key('summary'):
            self.vars['description'] = self.metadata['summary']
        else:
            self.vars['description'] = ''
        if self.vars['description']:
            self.vars['description'] = self.vars['description'].replace('"', "'")
    
        my_license = ""
        if self.metadata.has_key('classifiers'):
            for data in self.metadata['classifiers']:
                if data.startswith("License :: "):
                    my_license = get_portage_license(data)
        if not my_license:
            if self.metadata.has_key('License'):
                my_license = self.metadata['License']
            elif self.metadata.has_key('license'):
                my_license = self.metadata['license']
            my_license = "%s" % my_license
        if not is_valid_license(my_license):
            self.add_warning("Invalid LICENSE")
        self.vars['license'] = "%s" % my_license


        if self.metadata.has_key('Home-page'):
            self.vars['homepage'] = self.metadata['Home-page']
        elif self.metadata.has_key('home_page'):
            self.vars['homepage'] = self.metadata['home_page']
        elif self.metadata.has_key('home-page'):
            self.vars['homepage'] = self.metadata['home-page']
        else:
            self.vars['homepage'] = ''

    def add_warning(self, warning):
        """Add warning to be shown after ebuild is created"""
        if warning not in self.warnings:
            self.warnings.append(warning)

    def post_unpack(self):
        """Analyze unpacked package for:
           
           tests

           setup.py:
           PYTHON_MODNAME != $PN
           setuptools install_requires or extra_requires

        """
        name_regex = re.compile('''.*name\s*=\s*[',"]([\w+,\-,\_]*)[',"].*''')
        module_regex = \
               re.compile('''.*packages\s*=\s*\[[',"]([\w+,\-,\_]*)[',"].*''')

        nose_test = '''\tPYTHONPATH=. "${python}" setup.py nosetests || die "tests failed"'''
        regular_test = '''\tPYTHONPATH=. "${python}" setup.py test || die "tests failed"'''
        module_name = package_name = None

        if os.path.exists(self.unpacked_dir):
            setup_file = os.path.join(self.unpacked_dir, "setup.py")
            if not os.path.exists(setup_file):
                self.add_warning("No setup.py found!")
                return ""
            setup = open(setup_file, "r").readlines()
            for line in setup:
                name_match = name_regex.match(line)
                if name_match:
                    package_name = name_match.group(1)
                elif "packages" in line:
                    #grab first one
                    mods = line.split(",")[0]
                    module_match = module_regex.match(mods)
                    if module_match:
                        module_name = module_match.group(1)
                elif "install_requires" in line:
                    self.add_warning(line)
            
                elif "nose.collector" in line:
                    self.add_depend("test? ( dev-python/nose )")
                    self.add_use("test")
                    return nose_test
            if module_name and package_name:
                #    if module_name != package_name:
                self.python_modname = module_name

            if os.path.exists(os.path.join(self.unpacked_dir, "tests")) or os.path.exists(os.path.join(self.unpacked_dir, "test")):
                return regular_test

    def add_use(self, use_flag):
        """Add DEPEND"""
        self.use.append(use_flag)

    def add_depend(self, depend):
        """Add DEPEND"""
        self.depends.append(depend)

    def add_rdepend(self, rdepend):
        """Add RDEPEND"""
        self.rdepends.append(rdepend)

    def make_ebuild_file(self):
        """Generate ebuild from template"""
        #pylint: disable-msg=W0612
        #pylint thinks these are unused variables but we use locals()
        src_unpack = ""
        src_compile = ""
        src_install = ""
        src_test = self.post_unpack() 
        s = ""
        python_modname = ""

        depend = "\t".join(self.depends)
        rdepend = "\t".join(self.rdepends)
        if self.python_modname != self.vars['pn']:
            python_modname = self.python_modname
        use = " ".join(self.use)
        if self.s:
            s = self.s
        slot = "0"
        need_python = None
        year = localtime()[0]
        #Add homepage, license and description from metadata
        self.add_metadata()

        template = resource_string(__name__, EBUILD_TEMPLATE)
        self.ebuild_text = str(Template(template, searchList=[self.vars, locals()]))

    def create_ebuild(self):
        """Write ebuild and update it after unpacking and examining ${S}"""
        self.write_ebuild()
        self.update_with_s()
        #Write ebuild again after unpacking and adding ${S}
        self.make_ebuild_file()
        self.overwrite = True
        self.write_ebuild()
        self.show_warnings()
        self.logger.info("Your ebuild is here: " + self.ebuild_path)

    def write_ebuild(self):
        """Write ebuild file"""
        ebuild_dir = make_overlay_dir(self.category, self.vars['pn'], self.config['overlay'])
        if ebuild_dir:
            self.ebuild_path = os.path.join(ebuild_dir, "%s.ebuild" % self.vars['p'])
            if os.path.exists(self.ebuild_path) and not self.overwrite:
                self.logger.error("Ebuild exists. Use -o to overwrite.")
                self.logger.error(self.ebuild_path)
                sys.exit(2)
            out = open(self.ebuild_path, "w")
            out.write(self.ebuild_text)
            out.close()
        else:
            self.logger.error("Couldn't create overylay ebuild directory.")
            return 2

    def show_warnings(self):
        """Print warnings for incorrect ebuild syntax"""
        for warning in self.warnings:
            self.logger.warn("* Warning: %s" % warning)

    def update_with_s(self):
        """Add ${S} to ebuild if needed"""
        self.logger.debug("Trying to determine ${S}, unpacking...")
        unpack_ebuild(self.ebuild_path)
        unpacked_dir = find_s_dir(self.vars['p'], self.category)
        self.unpacked_dir = os.path.join(get_workdir(self.vars['p'], 
            self.category), unpacked_dir)
        if unpacked_dir and unpacked_dir != self.vars['p']:
            if unpacked_dir == self.vars['my_p_raw']:
                unpacked_dir = '${MY_P}'
            elif unpacked_dir == self.vars['my_pn']:
                unpacked_dir = '${MY_PN}'
            elif unpacked_dir == self.vars['pn']:
                unpacked_dir = '${PN}'

            self.s = "${WORKDIR}/%s" % unpacked_dir

def get_portage_license(my_license):
    """Map defined classifier license to Portage license

    http://cheeseshop.python.org/pypi?%3Aaction=list_classifiers
    """
    my_license = my_license.split(":: ")[-1:][0]
    known_licenses = {
        "Aladdin Free Public License (AFPL)": "Aladdin",
        "Academic Free License (AFL)": "AFL-3.0",
        "Apache Software License": "Apache-2.0",
        "Apple Public Source License": "Apple",
        "Artistic License": "Artistic-2",
        "BSD License": "BSD-2",
        "Common Public License": "CPL-1.0",
        "GNU Free Documentation License (FDL)": "FDL-3",
        "GNU General Public License (GPL)": "GPL-2",
        "GNU Library or Lesser General Public License (LGPL)": "LGPL-2.1",
        "IBM Public License": "IBM",
        "Intel Open Source License": "Intel",
        "MIT License": "MIT",
        "Mozilla Public License 1.0 (MPL)": "MPL",
        "Mozilla Public License 1.1 (MPL 1.1)": "MPL-1.1",
        "Nethack General Public License": "nethack",
        "Open Group Test Suite License": "OGTSL",
        "Python License (CNRI Python License)": "PYTHON",
        "Python Software Foundation License": "PSF-2.4",
        "Qt Public License (QPL)": "QPL",
        "Sleepycat License": "DB",
        "Sun Public License": "SPL",
        "University of Illinois/NCSA Open Source License": "ncsa-1.3",
        "W3C License": "WC3",
        "zlib/libpng License": "ZLIB",
        "Zope Public License": "ZPL",
        "Public Domain": "public-domain"
        }
    if known_licenses.has_key(my_license):
        return known_licenses[my_license]
    else:
        return ""

def is_valid_license(my_license):
    """Check if license string matches a valid one in ${PORTDIR}/licenses"""
    return os.path.exists(os.path.join(get_portdir(), "licenses", my_license))
