# -*- coding: utf-8 -*-
#
# File: __init__.py
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

import transaction
from thread import allocate_lock

from zope import interface
from zope import component
from zope.filerepresentation.interfaces import IFileFactory

from Products.CMFPlone import utils as ploneutils
from Products.CMFCore import utils as cmfutils

from interfaces import IUploadingCapable

upload_lock = allocate_lock()


class UploadingCapableFileFactory(object):
    interface.implements(IFileFactory)
    component.adapts(IUploadingCapable)

    def __init__(self, context):
        self.context = context

    def __call__(self, name, content_type, data):
        plone_tool = cmfutils.getToolByName(self.context, 'plone_utils')
        ctr = cmfutils.getToolByName(self.context, 'content_type_registry')
        type_ = ctr.findTypeName(name, '', '') or 'File'
        newid = plone_tool.normalizeString(name)

        # otherwise I get ZPublisher.Conflict ConflictErrors
        # when uploading multiple files
        upload_lock.acquire()
        try:
            transaction.begin()
            obj = ploneutils._createObjectByType(type_, self.context, newid)
            mutator = obj.getPrimaryField().getMutator(obj)
            mutator(data, content_type=content_type)
            obj.setTitle(name)
            transaction.commit()
        finally:
            upload_lock.release()
        return obj

# vim: set ft=python ts=4 sw=4 expandtab :
