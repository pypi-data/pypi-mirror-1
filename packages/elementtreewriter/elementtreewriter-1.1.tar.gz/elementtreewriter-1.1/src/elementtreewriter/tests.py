# -*- coding: utf-8 -*-
#
# Copyright (c) Törggelen Sprint Team, Bolzano
#
# German Free Software License (D-FSL)
#
# This Program may be used by anyone in accordance with the terms of the 
# German Free Software License
# The License may be obtained under <http://www.d-fsl.org>.

__author__ = """Jens Klein <jens@bluedynamics.com>"""

import code
import sys
import doctest
import unittest
import elementtreewriter

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE

def interact(locals=None):
    """Provides an interactive shell aka console inside your testcase.
    
    It looks exact like in a doctestcase and you can copy and paste
    code from the shell into your doctest. The locals in the testcase are 
    available, because you are _in_ the testcase.

    In your testcase or doctest you can invoke the shell at any point by
    calling::
        
        >>> interact( locals() )        
        
    locals -- passed to InteractiveInterpreter.__init__()
    """
    savestdout = sys.stdout
    sys.stdout = sys.stderr
    sys.stderr.write('\n'+'='*70)
    console = code.InteractiveConsole(locals)
    console.interact("""
DocTest Interactive Console - (c) BlueDynamics Alliance, Austria, 2006-2007
Note: You have the same locals available as in your test-case. 
Ctrl-D ends session and continues testing.
""")
    sys.stdout.write('\nend of DocTest Interactive Console session\n')
    sys.stdout.write('='*70+'\n')
    sys.stdout = savestdout 
    

def test_suite():
    return doctest.DocFileSuite('xmlwriter.txt',
                                 optionflags=doctest.ELLIPSIS + \
                                             doctest.REPORT_ONLY_FIRST_FAILURE)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite') 