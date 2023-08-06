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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.CMFCore import permissions
from Products.PortalTransforms.transforms.safe_html import register
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName

from italianskin.tool.config import *

schema = Schema((

    StringField(
        name='validator_url',
        default='http://validator.w3.org/check',
        widget=StringWidget(
            label='URL validator',
            label_msgid='ItalianSkin_label_validator_url',
            description='URL del validatore che si vuole utilizzare (default: w3c)',
            description_msgid='ItalianSkin_help_validator_url',
            i18n_domain='ItalianSkin',
        ),
        required=1,
    ),

    BooleanField(
        name='validation_action_enabled',
        default=True,
        accessor='isValidationActionEnabled',
        widget=BooleanWidget(
            label='Attiva la validazione integrata del codice',
            label_msgid='ItalianSkin_label_validationactionenabled',
            description='Attivando questa opzione avrai a disposizione uno strumento per la validazione integrata del codice',
            description_msgid='ItalianSkin_help_validationactionenabled',
            i18n_domain='ItalianSkin',
        )
    ),

    LinesField(
        name='class_titles',
        default=('Large','Normal','Small','Plone Default (contrast improved)',
                 'High Contrast (background black)', 'High Contrast (background black - Padding/fonts modified)'),
        widget=LinesWidget(
            label='Class titles',
            label_msgid='italianskin.tool_label_class_titles',
            description='Add your CSS class titles',
            description_msgid='italianskin.tool_help_class_titles',
            i18n_domain='italianskin.tool',
        ),
        required=1
    ),
    LinesField(
        name='css_classes',
        default=('largeText','normalText','smallText','HighContrast','HighContrastBlack','HighContrastBlackPadding'),
        widget=LinesWidget(
            label='CSS Classes',
            label_msgid='italianskin.tool_label_css_classes',
            description='Add your CSS class ids',
            description_msgid='italianskin.tool_help_css_classes',
            i18n_domain='italianskin.tool',
        ),
        required=1
    ),



),
)


ItalianSkinTool_schema = BaseSchema.copy() + \
    schema.copy()

ItalianSkinTool_schema['title'].widget.visible = {'edit': 'hidden', 'view': 'hidden'}

class ItalianSkinTool(UniqueObject, BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(UniqueObject,'__implements__',()),) + (getattr(BaseContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'ItalianSkinTool'

    meta_type = 'ItalianSkinTool'
    portal_type = 'ItalianSkinTool'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    content_icon = 'italianskin_tool.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "ItalianSkinTool"
    typeDescMsgId = 'description_edit_italianskintool'
    toolicon = 'italianskin_tool.gif'

    _at_rename_after_creation = True

    schema = ItalianSkinTool_schema

    actions =  (
       {'action': "string:${object_url}/is_tool_view",
        'category': "object",
        'id': 'view',
        'name': 'View',
        'permissions': ("View",),
        'condition': 'python:0'
       },
       {'id': 'metadata',
        'name': 'Properties',
        'action': 'string:${object_url}/base_metadata',
        'permissions': (permissions.ModifyPortalContent,),
        'condition': 'python:0'
       },
       {'id': 'edit',
        'name': 'Edit',
        'action': 'string:${object_url}/is_tool_view',
        'permissions': (permissions.ModifyPortalContent,),
        'condition': 'python:0'
       },
      )

    # tool-constructors have no id argument, the id is fixed
    def __init__(self, id=None):
        BaseContent.__init__(self,'portal_italianskintool')
        self.setTitle('ItalianSkinTool')

    security.declarePrivate('setValidation_action_enabled')
    def setValidation_action_enabled(self, value):
        ## ATTENZIONE: codice copiato e incollato cosi'com'era dalla vecchia versione, manca ancora l'azione da installare via GS
        valid_new_value = int(value)
        if valid_new_value:
            from Products.ItalianSkin.utils.action_utils import install_actions
            install_actions(self)
        else:
            from Products.ItalianSkin.utils.action_utils import uninstall_actions
            uninstall_actions(self)

        field = self.getField('validation_action_enabled')
        field.set(self, valid_new_value)

    def getValidationResults(self, xhtml):
        # Struttura dati ritornata
        #{'m:errors':{
        #             'm:errorcount':2,
        #             'm:errorlist':[
        #                            {'m:error':{
        #                                        'm:line':1,
        #                                        'm:col':2,
        #                                        'm:message':'messaggio errore',
        #                                       },
        #                            },
        #                            {'m:error':{
        #                                        'm:line':20,
        #                                        'm:col':1,
        #                                        'm:message':'altro messaggio errore',
        #                                       },
        #                            },
        #                           ],
        #            },
        #'m:warnings':{
        #              'm:warningcount':1,
        #              'm:warninglist':[
        #                               {'m:warning':{
        #                                             'm:line':1,
        #                                             'm:col':2,
        #                                             'm:message':'messaggio warning',
        #                                            },
        #                                },
        #                               ],
        #              }
        #}
        # Esiste un modo migliore?!

        ## ATTENZIONE: codice copiato e incollato cosi'com'era dalla vecchia versione, manca ancora l'azione da installare via GS
        results = {'m:errors':{'m:errorcount':0,
                               'm:errorlist':[],
                              },
                   'm:warnings':{'m:warningcount':0,
                                 'm:warninglist':[],
                                },
                   'm:validity':None,
                  }
        from xml.dom import minidom
        import urllib
        params = urllib.urlencode({'fragment': xhtml, 'verbose':'1', 'output':'soap12'})
        try:
            f = urllib.urlopen(self.getValidator_url(), params)
        except IOError:
            # validatore remoto non raggiungibile
            return results
        xmldoc = minidom.parseString(f.read())
        errors = xmldoc.getElementsByTagName('m:error')
        err_results = []
        for err in errors:
            diz = {}
            diz['m:line'] = int(err.getElementsByTagName('m:line')[0].childNodes[0].nodeValue)
            diz['m:col'] = int(err.getElementsByTagName('m:col')[0].childNodes[0].nodeValue)
            diz['m:message'] = err.getElementsByTagName('m:message')[0].childNodes[0].nodeValue
            err_results.append(diz)
        errs = results['m:errors']
        errs['m:errorcount'] = len(err_results)
        errs['m:errorlist'] = err_results
        results['m:errors'] = errs

        warnings = xmldoc.getElementsByTagName('m:warning')
        warn_results = []
        for warn in warnings:
            diz = {}
            diz['m:line'] = int(warnings.getElementsByTagName('m:line')[0].childNodes[0].nodeValue)
            diz['m:col'] = int(warnings.getElementsByTagName('m:col')[0].childNodes[0].nodeValue)
            diz['m:message'] = warnings.getElementsByTagName('m:message')[0].childNodes[0].nodeValue
            warn_results.append(diz)
        warns = results['m:warnings']
        warns['m:warningcount'] = len(warn_results)
        warns['m:warninglist'] = warn_results
        results['m:warnings'] = warns

        results['m:validity'] = xmldoc.getElementsByTagName('m:validity')[0].childNodes[0].nodeValue == 'true'
        return results


    security.declarePublic('getStyles')
    def getStyles(self):
        """ Ritorna una lista di dizionari elaborata in base alla configurazione immessa. Chiave: classe. Valore: titolo """
        classes = self.getCss_classes() 
        styles = self.getClass_titles()
        items = zip(classes, styles)
        
        results = []
        for item in items:
            results.append({'title':item[1], 'class':item[0]})
        return results

    # tool should not appear in portal_catalog
    def at_post_edit_script(self):

        self.unindexObject()
        

registerType(ItalianSkinTool, PROJECTNAME)



