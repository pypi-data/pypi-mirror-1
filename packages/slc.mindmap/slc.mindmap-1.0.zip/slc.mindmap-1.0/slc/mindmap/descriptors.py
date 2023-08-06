from zope import interface
from p4a.subtyper import interfaces as stifaces
from slc.mindmap import interfaces

class MindMapDescriptor(object):
    """A descriptor for the mindmap subtype.

      >>> descriptor = MindMapDescriptor()
      >>> descriptor.title
      u'MindMap'
    """

    interface.implements(stifaces.IPortalTypedDescriptor)
    title = u'MindMap'
    description = u''
    type_interface = interfaces.IMindMapDescriptor
    for_portal_type = 'File'
