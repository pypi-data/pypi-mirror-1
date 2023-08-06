from zope.app.content.interfaces import IContentType 
from zope.i18nmessageid import MessageFactory
from zope import interface
from zope import schema

_ = MessageFactory('slc.mindmap')

class IMindMapDescriptor(interface.Interface):
    """A new MindMap File subtype."""

interface.alsoProvides(IMindMapDescriptor, IContentType)


class IMindMeisterConfiguration(interface.Interface):
    """ This interface defines the dublettefinder configlet.
    """
    api_key = schema.TextLine(
        title=_(u"Your MindMeister API Key"),
        description=_(u"You need an API key from MindMeister.com to be able \
                        to embed their mind map editor. \
                        Register at www.mindmeister.com to get it."),
        default=u'',
        required=True,
        )

    mm_editor_url = schema.TextLine(
        title=_(u"MindMeister Embed URL"),
        description=_(u"The mindmeister.com URL to which a POST request must be \
                        made to open the editor window. You should not normally \
                        have to change this.\
                        See: http://www.mindmeister.com/services/api/embed"),
        default=u'http://www.mindmeister.com/external/show',
        required=True,
        )

    view_only = schema.Bool(
        title=_(u"Mind maps are not editable"),
        description=_(u"Enable this feature if you want to disable map editing via \
                        the embedded MindMeister editor."),
        default=True,
        required=True,
        )

    allow_export = schema.Bool(
        title=_(u"Allow exporting of Mind maps"),
        description=_(u"Enable this feature if you want to allow users to export \
                        mind maps via the embedded MindMeister editor."),
        default=False,
        required=True,
        )
    
    post_file = schema.Bool(
        title=_(u"Post the file to Mindmeister.com"),
        description=_(u"Enable this option if your site is behind a firewall \
                        or on a local offline instance that is not accessible \
                        by Mindmeister.com. \
                        Editing and exporting will be disabled with this \
                        feature. \
                        This option is not recommened for production systems."),
        default=True,
        required=True,
        )

