# -*- coding: utf-8 -*-
#
# File: upload.py
#
# Copyright (c) InQuant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__author__ = 'Ramon Bartl <ramon.bartl@inquant.de>'
__docformat__ = 'plaintext'

import logging
import mimetypes
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.filerepresentation.interfaces import IFileFactory

logger = logging.getLogger("collective.uploadify")


class Upload(BrowserView):
    """ The Upload View
    """

    template = ViewPageTemplateFile("upload.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        file_name = self.request.form.get("Filename", "")
        file_data = self.request.form.get("Filedata", None)
        content_type = mimetypes.guess_type(file_name)[0]

        if file_data:
            factory = IFileFactory(self.context)
            logger.info("uploading file: filename=%s, content_type=%s" % (file_name, content_type))
            f = factory(file_name, content_type, file_data)

        return self.template()

# vim: set ft=python ts=4 sw=4 expandtab :
