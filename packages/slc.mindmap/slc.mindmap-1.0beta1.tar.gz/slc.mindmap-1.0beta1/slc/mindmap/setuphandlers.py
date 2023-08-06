import logging
import transaction
from Products.CMFCore.utils import getToolByName

from config import MindMeisterConfiguration
from config import DEPENDENCIES 

from interfaces import IMindMeisterConfiguration

log = logging.getLogger('slc.mindmap.setuphandlers.py')

def isNotCurrentProfile(self):
    return self.readDataFile("slc_mindmap_marker.txt") is None

def registerUtilities(context):
    if isNotCurrentProfile(context):
        return

    sm = context.getSite().getSiteManager()
    if not sm.queryUtility(IMindMeisterConfiguration, 
                           name="mindmeister-settings",
                           ):

        sm.registerUtility(MindMeisterConfiguration(),
                           IMindMeisterConfiguration,
                           "mindmeister-settings",
                           )


# Cruft that cannot be gotten rid of without causing missing import steps in
# the portal_setup tool of systems that had an older version of slc.mindmap installed.
def set_file_default_view(context):
    """ """
    return

def uninstall(context):
    """ """
    return

