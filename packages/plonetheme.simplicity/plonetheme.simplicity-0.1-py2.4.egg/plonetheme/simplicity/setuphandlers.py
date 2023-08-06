from zope.component import getUtility, getMultiAdapter
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

def setPortlets(portal):
      """Since there's not GenericSetup way to do this"""
      left_column = getUtility(IPortletManager, name=u"plone.leftcolumn")
      left_assignable = getMultiAdapter((portal, left_column), IPortletAssignmentMapping)
      right_column = getUtility(IPortletManager, name=u"plone.rightcolumn")
      right_assignable = getMultiAdapter((portal, right_column), IPortletAssignmentMapping)
       # We move all portlets from left to right side
       # Don't know if this is a good idea, but the theme layout being so narrow
       # calls for it
      for name in left_assignable.keys():
            right_assignable[name] = left_assignable[name]
            del left_assignable[name]

def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('plonetheme.simplicity_various.txt') is None:
      return

    # Add additional setup code here
    portal = context.getSite()
    setPortlets(portal)
