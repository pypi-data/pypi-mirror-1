from Testing import ZopeTestCase as ztc
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

ztc.installProduct('PloneFormGen')

@onsetup
def setup_package():
    # roadrunner is not working without these 2 lines
    import Products.PloneFormGen
    zcml.load_config('configure.zcml', Products.PloneFormGen)

    fiveconfigure.debug_mode = True
    import quintagroup.ploneformgen.readonlystringfield
    zcml.load_config('configure.zcml',
        quintagroup.ploneformgen.readonlystringfield)
    fiveconfigure.debug_mode = False

    ztc.installPackage('quintagroup.ploneformgen.readonlystringfield')

setup_package()
ptc.setupPloneSite(products=['quintagroup.ploneformgen.readonlystringfield',])


class ReadOnlyStringFieldTestCase(ptc.PloneTestCase):
    """Common test base class"""


class ReadOnlyStringFieldFunctionalTestCase(ptc.FunctionalTestCase):
    """Common functional test base class"""
