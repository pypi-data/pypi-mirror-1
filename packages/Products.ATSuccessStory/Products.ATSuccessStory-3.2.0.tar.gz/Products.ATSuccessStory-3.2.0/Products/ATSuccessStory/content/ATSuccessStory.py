# -*- coding: utf-8 -*-
#
# File: ATSuccessStory.py
#
# Copyright (c) 2008 by []
# Generator: ArchGenXML Version 2.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Franco Pellegrini <frapell@menttes.com>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces
from Products.ATSuccessStory.content.ATSuccessStoryFolder import ATSuccessStoryFolder
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATSuccessStory.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    TextField(
        name='Story',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        widget=RichWidget(
            label='Story',
            label_msgid='ATSuccessStory_label_Story',
            i18n_domain='ATSuccessStory',
        ),
        default_output_type='text/html',
        required=1,
    ),
    ImageField(
        name='Image',
        widget=ImageField._properties['widget'](
            label='Image',
            label_msgid='ATSuccessStory_label_Image',
            i18n_domain='ATSuccessStory',
        ),
        required=1,
        storage=AttributeStorage(),
        sizes={'large' : (768, 768), 'preview' : (400, 400), 'mini' : (200, 200), 'atss' : (185, 185), 'thumb' : (128, 128), 'tile' : (64, 64), 'icon' : (32, 32), 'listing' : (16, 16),},
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

ATSuccessStory_schema = BaseSchema.copy() + \
    getattr(ATSuccessStoryFolder, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class ATSuccessStory(BaseContent, ATSuccessStoryFolder, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IATSuccessStory)

    meta_type = 'ATSuccessStory'
    _at_rename_after_creation = True

    schema = ATSuccessStory_schema

    ##code-section class-header #fill in your manual code here
    #security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('Image').tag(self, **kwargs)
    ##/code-section class-header

    # Methods

registerType(ATSuccessStory, PROJECTNAME)
# end of class ATSuccessStory

##code-section module-footer #fill in your manual code here
##/code-section module-footer



