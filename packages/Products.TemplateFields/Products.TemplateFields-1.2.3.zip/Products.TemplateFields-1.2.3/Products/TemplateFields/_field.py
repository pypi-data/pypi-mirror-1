##############################################################################
#
# TemplateFields - DTML and ZPT fields for Archetypes
# Copyright (C) 2005 Klein & Partner KEG
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
##############################################################################
"""
$Id: _field.py 10410 2009-01-23 11:46:44Z ivo $
"""

from zope.i18nmessageid import MessageFactory as mf
import types
from AccessControl import ClassSecurityInfo
from OFS.DTMLMethod import DTMLMethod
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from Products.Archetypes.public import ObjectField, TextAreaWidget
from Products.Archetypes.Registry import registerField
from Products.TemplateFields import config

_ = mf("plone")


_marker = []

class DTMLField(ObjectField):

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type' : 'dtml',
        'default': '<dtml-var title_or_id>',
        'default_content_type' : 'text/plain',
        'required': True,
        'widget': TextAreaWidget(visible={'view': 'invisible',
                                          'edit': 'visible'}),
        'validators': ('dtmlvalidator',)
        })

    security  = ClassSecurityInfo()

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        dtml = ObjectField.get(self, instance, **kwargs)
        if not kwargs.has_key('client'):
            kwargs['client'] = instance
        value = dtml(**kwargs)
        return value

    security.declarePrivate('getRaw')
    def getRaw(self, instance, **kwargs):
        dtml = ObjectField.get(self, instance, **kwargs)
        if getattr(dtml, 'read', _marker) is not _marker:
            return dtml.read()
        else:
            return dtml

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        if not isinstance(value, DTMLMethod):
            dtml = DTMLMethod(self.getName())
            dtml.munge(value)
            value = dtml
        ObjectField.set(self, instance, value, **kwargs)

    def getDefault(self, instance):
        value = ObjectField.getDefault(self, instance)
        dtml = DTMLMethod(self.getName())
        dtml.munge(value)
        return dtml.__of__(instance)


registerField(
    DTMLField,
    title="DTML Field",
    description=("A field that stores and renders DTML Methods")
    )


class ZPTField(ObjectField):

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type' : 'zpt',
        'default': '<span tal:replace="here/title_or_id" />',
        'default_content_type' : 'text/plain',
        'required': True,
        'widget': TextAreaWidget(visible={'view': 'invisible',
                                          'edit': 'visible'}),
        'validators': ('zptvalidator',)
        })

    security  = ClassSecurityInfo()

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        value = ObjectField.get(self, instance, **kwargs)
        if type(value) in types.StringTypes:
            # migration from TextField
            zpt = ZopePageTemplate(self.getName())
            ObjectField.set(self, instance, zpt, **kwargs)
            value = ObjectField.get(self, instance, **kwargs)
        if config.CATCH_RENDER_ERRORS:
            try:
                return value.pt_render(extra_context={'options': kwargs})
            except Exception, e:
                return _(u"zpt_field_render_error",
                         default=u'<div class="error">An error occured while rendering this field</div>')
        else:
            return value.pt_render(extra_context={'options': kwargs})

    security.declarePrivate('getRaw')
    def getRaw(self, instance, **kwargs):
        zpt = ObjectField.get(self, instance, **kwargs)
        if getattr(zpt, 'read', _marker) is not _marker:
            return zpt.read()
        else:
            return zpt

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        if not isinstance(value, ZopePageTemplate):
            zpt = ZopePageTemplate(self.getName())
            zpt.write(value)
            value = zpt
        ObjectField.set(self, instance, value, **kwargs)

    def getDefault(self, instance):
        value = ObjectField.getDefault(self, instance)
        zpt = ZopePageTemplate(self.getName())
        zpt.write(value)
        return zpt.__of__(instance)


registerField(
    ZPTField,
    title="ZPT Field",
    description=("A field that stores and renders Page Templates")
    )
