import transaction
from AccessControl import SecurityManagement
from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase import layer
from Testing import ZopeTestCase as ztc

# Ourselves
import Products.plonehrm
# Regular components
import plonehrm.checklist
import plonehrm.jobperformance
import plonehrm.notes
import plonehrm.contracts
try:
    import plonehrm.absence
except ImportError:
    plonehrm.absence = None


ptc.setupPloneSite()


def login_as_portal_owner(app):
    uf = app.acl_users
    owner = uf.getUserById(ptc.portal_owner)
    if not hasattr(owner, 'aq_base'):
        owner = owner.__of__(uf)
    SecurityManagement.newSecurityManager(None, owner)
    return owner


def get_portal():
    app = ztc.app()
    login_as_portal_owner(app)
    return getattr(app, ptc.portal_name)


class PlonehrmLayer(layer.PloneSite):

    @classmethod
    def setUp(cls):
        fiveconfigure.debug_mode = True
        zcml.load_config('configure.zcml',
                         Products.plonehrm)
        zcml.load_config('configure.zcml',
                         plonehrm.checklist)
        zcml.load_config('configure.zcml',
                         plonehrm.jobperformance)
        zcml.load_config('configure.zcml',
                         plonehrm.notes)
        zcml.load_config('configure.zcml',
                         plonehrm.contracts)
        if plonehrm.absence:
            zcml.load_config('configure.zcml',
                             plonehrm.absence)
        ztc.installProduct('plonehrm')
        ztc.installPackage('plonehrm.checklist')
        ztc.installPackage('plonehrm.jobperformance')
        #ztc.installPackage('plonehrm.notes')
        ztc.installPackage('plonehrm.contracts')
        if plonehrm.absence:
            ztc.installPackage('plonehrm.absence')

        portal = get_portal()
        portal.portal_quickinstaller.installProduct('plonehrm')

        transaction.commit()
        fiveconfigure.debug_mode = False


class MainTestCase(ptc.PloneTestCase):
    """Base TestCase for plonehrm."""

    layer = PlonehrmLayer
