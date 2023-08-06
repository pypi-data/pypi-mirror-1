from Testing import ZopeTestCase
from Products.PloneTestCase import ptc

from collective.testcaselayer import ptc as tcl_ptc

ptc.setupPloneSite()

class InstallLayer(tcl_ptc.BasePTCLayer):

    def afterSetUp(self):
        ZopeTestCase.installPackage('collective.redirect')
        self.addProfile('collective.redirect:default')
        
install_layer = InstallLayer([ptc.PloneTestCase.layer])
