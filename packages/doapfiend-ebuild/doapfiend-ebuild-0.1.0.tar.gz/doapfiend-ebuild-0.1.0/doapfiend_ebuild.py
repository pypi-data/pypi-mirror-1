#!/usr/bin/env python

# pylint: disable-msg=W0221,R0201
"""

doapfiend_ebuild
================

This is a plugin for creating Gentoo Linux ebuilds from DOAP

"""


import logging

from Cheetah.Template import Template

from doapfiend.plugins.base import Plugin
from doapfiend.doaplib import load_graph


__docformat__ = 'epytext'

LOG = logging.getLogger('doapfiend')


def get_license(license_url):
    '''
    Convert RDF license URL to Gentoo LICENSE

    '''
    license_url = license_url.strip()
    known_licenses = {
            'http://usefulinc.com/doap/licenses/artistic' : 'Artistic',
            'http://usefulinc.com/doap/licenses/asl20' : 'APSL-2',
            'http://usefulinc.com/doap/licenses/bsd' : 'BSD',
            'http://usefulinc.com/doap/licenses/gfdl' : 'FDL-3',
            'http://usefulinc.com/doap/licenses/gpl' : 'GPL-2',
            'http://usefulinc.com/doap/licenses/lgpl' : 'LGPL-2.1',
            'http://usefulinc.com/doap/licenses/mit' : 'MIT',
            'http://usefulinc.com/doap/licenses/mpl' : 'MPL',
            'http://usefulinc.com/doap/licenses/w3c' : 'WC3'
            }

    if known_licenses.has_key(license_url):
        return known_licenses[license_url]
    else:
        return ''


def make_ebuild(doap_xml):
    '''
    Create Gentoo ebuild from DOAP profile

    @param doap_xml: DOAP in RDF/XML serialization
    @type doap_xml: string

    @rtype: string
    @returns: ebuild

    '''
    doap = load_graph(doap_xml)
    if hasattr(doap, 'license') and len(doap.license) > 0:
        my_license = get_license(doap.license[0].resUri)
    else:
        my_license = ''
    if hasattr(doap, 'description') and len(doap.description) > 0:
        description = doap.description[0].strip(),
    else:
        description = ''

    my_vars = dict(description = description,
            homepage = doap.homepage.resUri,
            license = my_license,
            rdepend = '',
            depend = '',
            s = '',
            use = '',
            slot = '0',
            keywords = '~x86'
            )

    ebuild = Template(EBUILD_TEMPLATE, searchList=[my_vars])
    return ebuild.respond()


class EbuildPlugin(Plugin):

    """Class for formatting DOAP output"""

    name = "ebuild"
    enabled = False
    enable_opt = None

    def __init__(self):
        '''Setup EbuildPlugin class'''
        super(EbuildPlugin, self).__init__()
            
    def add_options(self, parser, output, search):
        '''Add plugin's options to doapfiend's opt parser'''
        output.add_option('--%s' % self.name,
                action='store_true', 
                dest=self.enable_opt,
                help='Create Gentoo ebuild from DOAP')
        return parser, output, search

    def serialize(self, doap_xml, color=False):
        '''
        Serialize DOAP as HTML

        @param doap_xml: DOAP in RDF/XML serialization
        @type doap_xml: string

        @param color: Syntax highlighting (Bash) with Pygments
        @type color: boolean 

        @rtype: unicode
        @returns: DOAP as HTML

        '''
        return make_ebuild(doap_xml)

#Cheetah template
EBUILD_TEMPLATE = '''
# Copyright 1999-2008 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# \$Header: \$

DESCRIPTION="$description"
HOMEPAGE="$homepage"
SRC_URI=""
LICENSE="$license"
KEYWORDS="$keywords"
SLOT="$slot"
IUSE="$use"
#if $s
S="$s"
#end if
#if $rdepend
RDEPEND="$rdepend"
#end if
#if $depend
DEPEND="$depend"
#end if

'''
