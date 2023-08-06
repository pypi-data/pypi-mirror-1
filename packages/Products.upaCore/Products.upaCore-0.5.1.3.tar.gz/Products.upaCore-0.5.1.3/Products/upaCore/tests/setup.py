from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

# Make sure the dummy types are registered

# and the types get still registered with the types tool
from Products.GenericSetup import EXTENSION, profile_registry

profile_registry.registerProfile('default',
    'SchemaExtenderDemo',
    'SchemaExtenderDemo',
    'profiles/default',
    'Products.SchemaExtenderDemo',
    EXTENSION)


ZopeTestCase.installProduct('Five')
ZopeTestCase.installProduct('ZWiki')
ZopeTestCase.installProduct('PloneFormGen')
ZopeTestCase.installProduct('FCKEditor')
ZopeTestCase.installProduct('TextIndexNG3')
ZopeTestCase.installProduct('membrane')
ZopeTestCase.installProduct('LinguaPlone')
ZopeTestCase.installProduct('Reflecto')
ZopeTestCase.installProduct('CMFBibliographyAT')
ZopeTestCase.installProduct('FileSystemStorage')
#ZopeTestCase.installProduct('Relations')
ZopeTestCase.installProduct('FacultyStaffDirectory')
ZopeTestCase.installProduct('SchemaExtenderDemo')
PROFILES = ['Products.SchemaExtenderDemo:default']

PloneTestCase.setupPloneSite(extension_profiles=PROFILES)

