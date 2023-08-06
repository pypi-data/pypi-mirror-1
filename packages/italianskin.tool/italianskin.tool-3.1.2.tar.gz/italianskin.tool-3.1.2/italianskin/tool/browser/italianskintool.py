# -*- coding: utf-8 -*-
#
# File: italianskintool.py
#
# Copyright (c) 2007 by Davide Moro (Redomino)
#
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
#

__author__ = """Davide Moro <davide.moro@redomino.com>"""
__docformat__ = 'plaintext'


from zope.interface import Interface
from zope.component import adapts
from zope.formlib.form import FormFields
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.controlpanel.form import ControlPanelForm

from italianskin.tool.interfaces import IItalianSkinToolSchema

class ItalianSkinToolControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IItalianSkinToolSchema)

    def __init__(self, context):
        super(ItalianSkinToolControlPanelAdapter, self).__init__(context)
        self.context = getToolByName(context, 'portal_italianskintool')

    def get_class_titles(self):
        return self.context.getClass_titles()

    def set_class_titles(self, value):
        self.context.setClass_titles(value)

    class_titles = property(get_class_titles, set_class_titles)

    def get_css_classes(self):
        return self.context.getCss_classes()

    def set_css_classes(self, value):
        self.context.setCss_classes(value)

    css_classes = property(get_css_classes, set_css_classes)


class ItalianSkinToolControlPanel(ControlPanelForm):

    form_fields = FormFields(IItalianSkinToolSchema)

    label = _("ItalianSkinTool settings")
    description = _("ItalianSkinTool settings that affect the site configuration.")
    form_name = _("ItalianSkinTool settings")
