from zope.component import getMultiAdapter, getUtility

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

def setupVarious(context):
    
    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a 
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    
    if context.readDataFile('webcouturier.hosting.theme_various.txt') is None:
        return
        
    logger=context.getLogger("webcouturier.hosting.theme")
    portal = context.getSite()
    removeRightPortlets(logger, portal)
    
def removeRightPortlets(logger, portal):
    logger.info("We need to un-assign portlets for the right column.")
    
    rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=portal)    
    right = getMultiAdapter((portal, rightColumn,), IPortletAssignmentMapping, context=portal)
    
    for portlet in right:
        del right[portlet]
        logger.info("Un-assigned %s portlet." % portlet)