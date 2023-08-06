from Testing import ZopeTestCase

from DateTime import DateTime

# Make the boring stuff load quietly
ZopeTestCase.installProduct('CMFCore', quiet=1)
ZopeTestCase.installProduct('CMFDefault', quiet=1)
ZopeTestCase.installProduct('CMFCalendar', quiet=1)
ZopeTestCase.installProduct('CMFTopic', quiet=1)
ZopeTestCase.installProduct('DCWorkflow', quiet=1)
ZopeTestCase.installProduct('CMFHelpIcons', quiet=1)
ZopeTestCase.installProduct('CMFQuickInstallerTool', quiet=1)
ZopeTestCase.installProduct('CMFFormController', quiet=1)
ZopeTestCase.installProduct('GroupUserFolder', quiet=1)
ZopeTestCase.installProduct('ZCTextIndex', quiet=1)
ZopeTestCase.installProduct('TextIndexNG2', quiet=1)
ZopeTestCase.installProduct('SecureMailHost', quiet=1)
ZopeTestCase.installProduct('CMFPlone')
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('PortalTransforms', quiet=1)
ZopeTestCase.installProduct('MimetypesRegistry', quiet=1)
ZopeTestCase.installProduct('Five', quiet=1)
ZopeTestCase.installProduct('kupu', quiet=1)
ZopeTestCase.installProduct('DataGridField', quiet=1)
ZopeTestCase.installProduct('contentmigrations', quiet=1)
ZopeTestCase.installProduct('ATSchemaEditorNG')
ZopeTestCase.installProduct('SignupSheet')

from Products.PloneTestCase import PloneTestCase

PRODUCTS = ['SignupSheet']

PloneTestCase.setupPloneSite(products=PRODUCTS)


class SignupSheetTestCase(PloneTestCase.PloneTestCase):

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()
        self.portal.email_from_address='postmaster@demo.netcorps.org'


    def createSignupSheet(self, folder, id, title='', description='',
                        eventSize=1,
                        waitList=2,
                        thank_you_text="Thank you",
                        text="One Great Event",
                        registrantProlog="Sign up",
                        ):
        """Create a new tracker in the given folder"""
        self.setRoles(['Manager'])
        folder.invokeFactory('SignupSheet', id)
        signupsheet = getattr(folder, id)
        signupsheet.setTitle(title)
        signupsheet.setDescription(description)
        signupsheet.setEventsize(eventSize)
        signupsheet.setWaitlist_size(waitList)
        signupsheet.setText(text)
        signupsheet.setThank_you_text(thank_you_text)
        signupsheet.setRegistrantProlog(registrantProlog)
        signupsheet.reindexObject()
        return signupsheet

    def createRegistrant(self, signupsheet, title='New Registrant', ):
        
        """Create an issue in the given signupsheet, and perform workflow and
        rename-after-creation initialisation"""
        #newId = self.portal.generateUniqueId('Registrant')
        #oldIds = signupsheet.objectIds()
        signupsheet.invokeFactory('Registrant', title)
        registrant = getattr(signupsheet, title)
        registrant.setTitle(title)
        registrant.setEmail('nowhere@localhost.org')
        #self.portal.portal_workflow.doActionFor(registrant, 'post')
        registrant._renameAfterCreation()
        registrant.reindexObject()
        return registrant
