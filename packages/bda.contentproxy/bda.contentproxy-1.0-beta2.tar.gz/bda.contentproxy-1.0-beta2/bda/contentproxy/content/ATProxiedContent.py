# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import implements
from zope.component.factory import Factory

from zope.i18nmessageid import MessageFactory

from AccessControl import ClassSecurityInfo

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.Archetypes.atapi import *

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget \
    import ReferenceBrowserWidget

import interfaces

_ = MessageFactory('bda.contentproxy')

schema = Schema((

    StringField(
        name='proxyreference',
        widget=ReferenceBrowserWidget(
            label="Proxy Reference",
            description="Select the reference of the content you want to proxy",
            label_msgid='bda_contentproxy_label_proxyreference',
            description_msgid='bda_contentproxy_help_proxyreference',
            i18n_domain='bda_contentproxy',
            required=True,
        ),
    ),
),
)

ATProxiedContent_schema = BaseSchema.copy() + \
    schema.copy()

class ATProxiedContent(BaseContent, BrowserDefaultMixin):
    
    security = ClassSecurityInfo()
    implements(interfaces.IATProxiedContent)

    meta_type = 'ATProxiedContent'
    _at_rename_after_creation = True

    schema = ATProxiedContent_schema


registerType(ATProxiedContent, 'bda.contentproxy')

addATProxiedContent = Factory(ATProxiedContent, title=_(u"Add Content Proxy"))



