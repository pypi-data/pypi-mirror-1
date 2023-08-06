from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase

from Products.ATVocabularyManager.config import *
from Products.ATVocabularyManager.Extensions.Install import install

from Products.SiteErrorLog.SiteErrorLog import manage_addErrorLog
from Products.Archetypes.Extensions.Install import install as installAT

PloneTestCase.setupPloneSite(id='plone')

def installProducts():
    ZopeTestCase.installProduct('Archetypes')
    ZopeTestCase.installProduct('MimetypesRegistry')
    ZopeTestCase.installProduct('PortalTransforms')
    # to support tests for translated vocabularies
    ZopeTestCase.installProduct('PloneLanguageTool')
    ZopeTestCase.installProduct('LinguaPlone')

    ZopeTestCase.installProduct(PROJECTNAME)


def installWithinPortal(portal):
    installAT(portal, include_demo=1)
    install(portal)

def getATVM(portal):
    return portal[TOOL_NAME]
