# -*- coding: utf-8 -*-
#

__author__ = """Horacio Duran <hduran@except.com.ar>"""
__docformat__ = 'plaintext'



import os, sys, code
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

##code-section module-header #fill in your manual code here
pgp_user = "auser"
pgp_password = "apassword"
from Products.PloneGetPaid.config import PLONE3
from Testing import ZopeTestCase
if not PLONE3:
    ZopeTestCase.installProduct('CMFonFive')
##/code-section module-header

from Products.PloneTestCase import PloneTestCase
from getpaid.formgen.config import PRODUCT_DEPENDENCIES
from getpaid.formgen.config import DEPENDENCIES

# Add common dependencies
DEPENDENCIES.append('Archetypes')
PRODUCT_DEPENDENCIES.append('MimetypesRegistry')
PRODUCT_DEPENDENCIES.append('PortalTransforms')
PRODUCT_DEPENDENCIES.append('PloneGetPaid')
PRODUCT_DEPENDENCIES.append('PloneFormGen')
PRODUCT_DEPENDENCIES.append('getpaid.formgen')

# Install all (product-) dependencies, install them too
for dependency in PRODUCT_DEPENDENCIES + DEPENDENCIES:
    ZopeTestCase.installProduct(dependency)

ZopeTestCase.installProduct('getpaid.formgen')

PRODUCTS = list()
PRODUCTS += DEPENDENCIES
PRODUCTS.append('getpaid.formgen')

testcase = PloneTestCase.PloneTestCase
##code-section module-before-plone-site-setup #fill in your manual code here
##/code-section module-before-plone-site-setup

PloneTestCase.setupPloneSite(products=PRODUCTS)

class base_test_case(testcase):
    """Base TestCase for getpaid.formgen."""

    ##code-section class-header_base_test_case #fill in your manual code here
    ##/code-section class-header_base_test_case

    # Commented out for now, it gets blasted at the moment anyway.
    # Place it in the protected section if you need it.
    #def afterSetup(self):
    #    """
    #    """
    #    pass

    def interact(self, locals=None):
        """Provides an interactive shell aka console inside your testcase.

        It looks exact like in a doctestcase and you can copy and paste
        code from the shell into your doctest. The locals in the testcase are
        available, becasue you are in the testcase.

        In your testcase or doctest you can invoke the shell at any point by
        calling::

            >>> self.interact( locals() )

        locals -- passed to InteractiveInterpreter.__init__()
        """
        savestdout = sys.stdout
        sys.stdout = sys.stderr
        sys.stderr.write('='*70)
        console = code.InteractiveConsole(locals)
        console.interact("""
ZopeTestCase Interactive Console
(c) BlueDynamics Alliance, Austria - 2005

Note: You have the same locals available as in your test-case.
""")
        sys.stdout.write('\nend of ZopeTestCase Interactive Console session\n')
        sys.stdout.write('='*70+'\n')
        sys.stdout = savestdout


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(base_test_case))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


