from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.publisher.interfaces import BadRequest

from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.browser.info import PASInfoView
from Products.Archetypes.utils import shasattr
from betahaus.debug import config

import logging
logger = logging.getLogger(config.PROJECTNAME)

from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod

def importVarious(context):

    if context.readDataFile('betahaus.debug.various.txt') is None:
        # don't run this step unless the betahaus.debug profile is being
        # applied
        return

    site = context.getSite()
    
    if not 'pdb' in site.objectIds():
        manage_addExternalMethod(site, 'pdb', 'Debug method', 'betahaus.debug.debug', 'pdb')
    