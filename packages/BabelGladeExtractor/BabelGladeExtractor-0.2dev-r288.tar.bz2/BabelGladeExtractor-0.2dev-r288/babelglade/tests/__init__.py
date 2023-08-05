# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: __init__.py 281 2007-08-20 08:47:20Z cmlenz $
# =============================================================================
#             $URL: http://svn.edgewall.org/repos/babel/contrib/glade/babelglade/tests/__init__.py $
# $LastChangedDate: 2007-08-20 09:47:20 +0100 (Mon, 20 Aug 2007) $
#             $Rev: 281 $
#   $LastChangedBy: cmlenz $
# =============================================================================
# Copyright (C) 2007 Ufsoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================


import unittest

def suite():
    from babelglade.tests import extract
    suite = unittest.TestSuite()
    suite.addTest(extract.suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
