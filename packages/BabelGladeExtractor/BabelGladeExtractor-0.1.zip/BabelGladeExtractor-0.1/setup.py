#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: setup.py 240 2007-07-20 16:27:17Z palgarvio $
# =============================================================================
#             $URL: http://svn.edgewall.org/repos/babel/contrib/BabelGladeExtractor/setup.py $
# $LastChangedDate: 2007-07-20 17:27:17 +0100 (Fri, 20 Jul 2007) $
#             $Rev: 240 $
#   $LastChangedBy: palgarvio $
# =============================================================================
# Copyright (C) 2006 Ufsoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

from setuptools import setup

setup(
    name    = 'BabelGladeExtractor',
    version = '0.1',
    license = 'BSD',
    author  = 'Pedro Algarvio',
    author_email = 'ufs@ufsoft.org',
    maintainer = 'Pedro Algarvio',
    maintainer_email = 'ufs@ufsoft.org',
    description = 'Babel Glade XML files translatable strings extractor',
    url = 'http://babel.edgewall.org/wiki/BabelGladeExtractor',
    keywords = ['PyGTK', 'Glade', 'gettext', 'Babel', 'I18n', 'L10n'],
    install_requires = ['Babel'],
    entry_points = """
    [babel.extractors]
    glade = babelglade:extract_glade
    """,
    packages = ['babelglade']

)
