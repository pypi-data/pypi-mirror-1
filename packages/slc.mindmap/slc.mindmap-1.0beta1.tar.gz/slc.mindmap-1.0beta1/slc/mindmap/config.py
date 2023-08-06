from zope.component import getUtility
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from OFS.SimpleItem import SimpleItem

from interfaces import IMindMeisterConfiguration

PROJECTNAME = "slc.mindmap"
GLOBALS = globals()

DEPENDENCIES = [
    'p4a.subtyper',
    ]

MM_FILE_KEY = 'file[content]'

MM_FILETYPES = {
        "mind": "MindMeister (.mind)",
        "mmap": "MindManager (.mmap)",
        "mm":   "FreeMind (.mm)",
    }

# The mindmeister.com error codes
MM_ERR_CODES = {
    20: ('Object not found', 'Object not found'),
    23: ('Missing Parameter', 'A required parameter is missing'),
    96: ('Invalid signature', 'The passed signature was invalid.'),
    97: ('Missing signature', 'The call required signing but no signature was sent.'),
    98: ('Login failed / Invalid auth token', 'The login details or auth token passed were invalid.'),
    100: ('Invalid API Key', 'The API key passed was not valid or has expired.'),
    108: ('Invalid frob', 'The specified frob does not exist or has already been used.'),
    112: ('Method not found', 'The requested method was not found.'),
}

class MindMeisterConfiguration(SimpleItem):
    implements(IMindMeisterConfiguration)

    api_key = FieldProperty(IMindMeisterConfiguration['api_key'])
    mm_editor_url = FieldProperty(IMindMeisterConfiguration['mm_editor_url'])
    view_only = FieldProperty(IMindMeisterConfiguration['view_only'])
    allow_export = FieldProperty(IMindMeisterConfiguration['allow_export'])
    post_file = FieldProperty(IMindMeisterConfiguration['post_file'])


def form_adapter(context):
    return getUtility(IMindMeisterConfiguration,
                      name='mindmeister-settings',
                      context=context)

