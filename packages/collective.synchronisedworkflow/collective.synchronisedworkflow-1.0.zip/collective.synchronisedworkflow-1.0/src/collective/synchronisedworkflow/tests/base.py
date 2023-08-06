from collective.testcaselayer import ptc as tcl_ptc
from Products.Five import zcml, fiveconfigure
from Products.PloneTestCase import ptc
from Testing import ZopeTestCase

class Layer(tcl_ptc.BasePTCLayer):
    """Install collective.foo"""

    def afterSetUp(self):
        ZopeTestCase.installPackage('collective.synchronisedworkflow')
        fiveconfigure.debug_mode = True
        import collective.synchronisedworkflow
        zcml.load_config("configure.zcml", collective.synchronisedworkflow)
        fiveconfigure.debug_mode = False
        #self.addProfile('collective.synchronisedworkflow:default')

installed = Layer([tcl_ptc.ptc_layer])
uninstalled = tcl_ptc.BasePTCLayer([tcl_ptc.ptc_layer])