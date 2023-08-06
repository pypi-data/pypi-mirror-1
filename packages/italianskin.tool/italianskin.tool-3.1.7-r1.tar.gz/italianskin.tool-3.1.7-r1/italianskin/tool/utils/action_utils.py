# -*- coding: utf-8 -*-
#
# File: ItalianSkinTool.py
#
# Copyright (c) 2007 by []
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

from Products.CMFCore.utils import getToolByName

def install_actions(self):
    ai = getToolByName(self, 'portal_actionicons')
    try:
        ai.getActionIcon('plone', 'validateXhtml')
    except KeyError:
        ai.addActionIcon('plone', 'validateXhtml', 'ItalianSkinValidation.gif', 'Validate XHTML code')

    pa = getToolByName(self, 'portal_actions')
    try:
        pa.getActionInfo('document_actions/validateXhtml')
    except ValueError:
        pa.addAction('validateXhtml',
                      name='Validate XHTML code',
                      action='string:${object_url}/validate_xhtml_form',
                      condition='python: object.portal_type in ["Document", "News", "Event"]',
                      permission='View',
                      category='document_actions')

def uninstall_actions(self):
    # Elimino icone/actions installate da IS
    ai = getToolByName(self, 'portal_actionicons')
    try:
        ai.removeActionIcon('plone', 'validateXhtml')
    except:
        pass

    pa = getToolByName(self, 'portal_actions')
    acts=list(pa.listActions())
    selection_indexes = [acts.index(a) for a in acts if a.id=='validateXhtml']
    pa.deleteActions(selection_indexes)
