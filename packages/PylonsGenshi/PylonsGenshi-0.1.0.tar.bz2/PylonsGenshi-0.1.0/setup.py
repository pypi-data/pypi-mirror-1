#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: setup.py 92 2008-01-07 00:05:55Z s0undt3ch $
# =============================================================================
#             $URL: http://pastie.ufsoft.org/svn/sandbox/PylonsGenshi/trunk/setup.py $
# $LastChangedDate: 2008-01-07 00:05:55 +0000 (Mon, 07 Jan 2008) $
#             $Rev: 92 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2007 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================


try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

VERSION = '0.1.0'

setup(
    name = 'PylonsGenshi',
    version = VERSION,
    description = 'Pylons Project Template Using Genshi As The ' + \
                  'Templating Language',
    long_description = open('README.txt').read(),
    keywords = 'web wsgi pylons framework genshi',
    license = 'BSD',
    author = 'Pedro Algarvio',
    author_email = 'ufs@ufsoft.org',
    url = 'http://pastie.ufsoft.org/wiki/PylonsGenshi',
    packages = find_packages(exclude=['ez_setup']),
    zip_safe = False,
    include_package_data = True,
    install_requires = ['Pylons', 'Genshi'],
    extras_require = { 'minification': ['MinificationWebHelpers'] },
    entry_points = """
    [paste.paster_create_template]
    pylonsgenshi = pylonsgenshi.template:PylonsGenshiTemplate
    """
)
