from zope.component import getUtility
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletManager

from webcouturier.city.theme.portlets import personaltools

def setupVarious(context):
    """Run the various non-Generic Setup profile import steps."""
    portal = context.getSite()
    configurePortlets(portal)

def configurePortlets(portal):
    
    leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn',
            context=portal)
    
    left = getMultiAdapter((portal, leftColumn,), IPortletAssignmentMapping,
            context=portal)           

    if u'personaltools' not in left:
        left[u'personaltools'] = personaltools.Assignment()

