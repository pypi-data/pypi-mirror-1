import zope
from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

# cache setup monkey patch can be annoying...
#try: 
#    from Products.CMFSquidTool import patch
#    def none(self, *args, **kwargs):pass
#    patch.run = none
#    patch.unwrap_method = none
#except Exception, e:
#    pass 
@onsetup
def setup_collective_z3cform_grok():
    """Set up the additional products required for the nmd.sugar) site policy.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    # ------------------------------------------------------------------------------------
    # Get five errors if any for making debug easy.
    # ------------------------------------------------------------------------------------
    fiveconfigure.debug_mode = True

    # ------------------------------------------------------------------------------------
    # Import all our python modules required by our packages
    # ------------------------------------------------------------------------------------
#with_ploneproduct_pz3cform
    import five.grok
    import plone.z3cform
    import plone.app.z3cform

    # ------------------------------------------------------------------------------------
    # - Load the ZCML configuration for the collective.z3cform.grok package.
    # ------------------------------------------------------------------------------------


#with_ploneproduct_pz3cform
    zcml.load_config('configure.zcml', five.grok)
#with_ploneproduct_facultystaff
    zcml.load_config('configure.zcml', plone.z3cform)
    zcml.load_config('configure.zcml', plone.app.z3cform)

    # ------------------------------------------------------------------------------------
    # - Load the python packages that are registered as Zope2 Products via Five
    #   which can't happen until we have loaded the package ZCML.
    # ------------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------------
    # Load our own policy
    # ------------------------------------------------------------------------------------
    import collective.z3cform.grok
    zcml.load_config('configure.zcml', collective.z3cform.grok)

    # ------------------------------------------------------------------------------------
    # Reset five debug mode as we do not use it anymore
    # ------------------------------------------------------------------------------------
    fiveconfigure.debug_mode = False




# The order here is important: We first call the (deferred) function which
# installs the products we need for the nmd.sugar package. Then, we let
# PloneTestCase set up this product on installation.

setup_collective_z3cform_grok()
ptc.setupPloneSite(products=[\
# if we have csvreplicata, just say that a plone site can't live without :)
    'csvreplicata',
    'collective.z3cform.grok']
)

class collective_z3cform_grok_PolicyTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """

class collective_z3cform_grok_PolicyFunctionalTestCase(ptc.FunctionalTestCase):
    """
    """
