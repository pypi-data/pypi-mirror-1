# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import sys
import random
import logging
from cStringIO import StringIO

import cookielib
import mimetools
import mimetypes
import urllib
import urllib2

from zope.component import getUtility

from Products.Five.browser import BrowserView

from slc.mindmap.interfaces import IMindMeisterConfiguration
from slc.mindmap.config import MM_FILETYPES
from slc.mindmap.config import MM_FILE_KEY as file_key

log = logging.getLogger('slc.mindmap.browser.mindmap.py')

class MindMeisterEditor(BrowserView):

    def __call__(self):
         return self.get_mm_editor()

    def get_mm_editor(self):
        """ see: http://www.mindmeister.com/services/api/embed
        """
        context = self.context
        file = context.getFile()
        mm_config = getUtility(IMindMeisterConfiguration,
                               name='mindmeister-settings')

        filename = file.filename
        extension = file.content_type.replace('application/', '').split('-')[-1] 
        if extension not in MM_FILETYPES.keys():
            if filename.split('.')[-1] in MM_FILETYPES.keys():
                extension = filename.split('.')[-1]
            else:
                # XXX: Return error template
                raise 'Could not get file extension'

        fields = {
            'api_key': mm_config.api_key, 
            'file[id]': '%d' % random.randint(0,1000),
            'file[name]': "'%s'" % context.getId(),
            'file[extension]': extension,
            'file[content]': file, 
            'file[hide_close_button]': 'on',
            'file[view_only]': 'on',
            }
        editor_url = mm_config.mm_editor_url
        cookies = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies),
                                      MultipartPostHandler)
        response = opener.open(editor_url, fields)
        html = response.read()

        # XXX: Hack because the links are relative
        html = html.replace(
            '<head>', 
            '<head><base href="http://www.mindmeister.com/external/show"/><!--[if lt IE 7]></base><![endif]-->')
        return html


class SaveMindMap(BrowserView):
    """ This class will be called by MindMeister.com when a mindmap is 
        saved via embedded editor.
    """

    def __call__(self):
        return self.save_mindmap()

    def save_mindmap(self):
        context = self.context
        request = self.context.request
        file = context.getFile()
        filename = file.getFilename()
        extension = file.content_type.replace('application/', '').split('-')[-1] 
        if extension not in MM_FILETYPES.keys():
            if filename.split('.')[-1] in MM_FILETYPES.keys():
                extension = filename.split('.')[-1]
            else:
                raise 'Could not get file extension'

        filename =  filename.rsplit(extension)[0] + 'mind'
        file = context.request.get(filename)
        if file is None:
            raise 'File not found'

        context.setFile(file)
        log.info('Mindmap succesfully saved!')
        return 'file saved!'


# References and Acknowledgements:
#   Upload files in python:
#       http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306
#   Unicode support:
#       http://peerit.blogspot.com/2007/07/multipartposthandler-doesnt-work-for.html
#   
#       Fabien Seisen: <fabien@seisen.org>
#       Will Holcomb <wholcomb@gmail.com>
#       Brian Schneider  

class MultipartPostHandler(urllib2.BaseHandler):
    """
    Usage:
    Enables the use of multipart/form-data for posting forms

    Example:
    import MultipartPostHandler, urllib2, cookielib

    cookies = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies),
                                  MultipartPostHandler)
    params = { "username" : "bob", "password" : "riviera",
                "file" : open("filename", "rb") }
    opener.open("http://wwww.bobsite.com/upload/", params)
    """
    handler_order = urllib2.HTTPHandler.handler_order - 10 # needs to run first

    def http_request(self, request):
        data = request.get_data()
        if data is not None and type(data) != str:
            v_files = []
            v_vars = []
            try:
                 for(key, value) in data.items():
                    if key == file_key:
                        v_files.append((key, value))
                    else:
                        v_vars.append((key, value))
            except TypeError:
                systype, value, traceback = sys.exc_info()
                raise TypeError, "not a valid non-string sequence or mapping object", traceback
            
            if len(v_files) == 0:
                # Controls how sequences are uncoded. If true, elements may be given multiple values by
                #  assigning a sequence.
                doseq = 1
                data = urllib.urlencode(v_vars, doseq)
            else:
                boundary, data = self.multipart_encode(v_vars, v_files)

                contenttype = 'multipart/form-data; boundary=%s' % boundary
                if(request.has_header('Content-Type')
                   and request.get_header('Content-Type').find('multipart/form-data') != 0):
                    print "Replacing %s with %s" % (request.get_header('content-type'), 'multipart/form-data')
                request.add_unredirected_header('Content-Type', contenttype)

            request.add_data(data)
        return request

    def multipart_encode(self, vars, files, boundary = None, buf = None):
        if boundary is None:
            boundary = mimetools.choose_boundary()
        if buf is None:
            buf = StringIO()
        for(key, value) in vars:
            buf.write('--%s\r\n' % boundary)
            buf.write('Content-Disposition: form-data; name="%s"' % key)
            buf.write('\r\n\r\n' + value + '\r\n')
        for(key, file) in files:
            filename = file.filename
            contenttype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            buf.write('--%s\r\n' % boundary)
            buf.write('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename))
            buf.write('Content-Type: %s\r\n' % contenttype)
            data = file.data
            if hasattr(data, 'data'):
                data = data.data

            buf.write('\r\n' + data + '\r\n')
        buf.write('--' + boundary + '--\r\n\r\n')
        buf = buf.getvalue()
        return boundary, buf

