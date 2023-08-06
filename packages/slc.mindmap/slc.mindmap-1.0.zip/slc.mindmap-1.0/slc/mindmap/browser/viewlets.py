import urllib
import random

from zope.component import getUtility

from plone.app.layout.viewlets.common import ViewletBase

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from slc.mindmap.config import MM_FILETYPES
from slc.mindmap.interfaces import IMindMeisterConfiguration

class MindMapViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/preview.pt')

    def call_api_method(self, base_url, **kw):
        parms = urllib.urlencode(kw)
        url = '%s?%s' % (base_url, parms)
        fp = urllib.urlopen(url)
        xml = fp.read()
        return xml

    def construct_url(self):
        """ Encode dictionary of paremters into an URL
        """
        context = self.context
        mm_config = getUtility(IMindMeisterConfiguration,
                               name='mindmeister-settings')

        if mm_config.post_file:
            return '%s/@@mindmeister_editor' % context.absolute_url() 

        file = context.getFile()
        filename = file.getFilename()
        extension = file.content_type.replace('application/', '').split('-')[-1] 
        if extension not in MM_FILETYPES.keys():
            if filename.split('.')[-1] in MM_FILETYPES.keys():
                extension = filename.split('.')[-1]
            else:
                # XXX: Return error template
                raise 'Could not get file extension'

        portal_url = getToolByName(context, 'portal_url')
        download_url = '%s/%s' % \
            (portal_url(), '/'.join(context.getPhysicalPath()[2:]))
        editor_url = mm_config.mm_editor_url

        # Mindmeister can only save (overwrite) their own mindmap format
        fields = {
            'api_key': mm_config.api_key, 
            'file[id]': random.randint(0,1000),
            'file[name]': filename.rsplit(extension)[0] + 'mind',
            'file[save_action]':  "'s'",
            'file[extension]': extension,
            'file[hide_close_button]': 'on',
            }

        if mm_config.allow_export:
            fields['file[allow_export]'] = 'on'

        if mm_config.view_only:
            fields['file[view_only]'] = 'on'

        data = urllib.urlencode(fields)
        data += '&file%%5Bdownload_url%%5D=%s' % download_url
        data += '&file%%5Bnewcopy_url%%5D=%s/save_mindmap' % download_url
        return '%s?%s' % (editor_url, data)



