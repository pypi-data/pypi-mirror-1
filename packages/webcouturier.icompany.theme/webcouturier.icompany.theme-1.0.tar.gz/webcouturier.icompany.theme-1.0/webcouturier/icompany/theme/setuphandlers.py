from zope.component import getUtility
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager

def setupVarious(context):
    """Run the various non-Generic Setup profile import steps."""
    portal = context.getSite()
    configurePortlets(portal)

def configurePortlets(portal):
    
    leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn',
            context=portal)
    
    left = getMultiAdapter((portal, leftColumn,), IPortletAssignmentMapping,
            context=portal)           

    if u'navigation' in left:
        # show navtree starting on the 3rd level only
        navigation = left['navigation']
        navigation.topLevel = 2

