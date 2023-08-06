# $Id: controlpanel.py 106618 2009-12-13 23:35:52Z glenfant $
"""Personalisation forms"""

from zope.interface import Interface, implements
from zope.component import adapts, getAdapter, getMultiAdapter
from zope.schema import Bool
from zope.formlib import form

from Products.Five.formlib import formbase
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone import PloneMessageFactory as p_

from aws.inlineuserpref import AWSInlineUserPrefMessageFactory as _

class IInlineEditOption(Interface):
    """Does the user prefer inline editing"""

    enable_inline_editing = Bool(
        title=_(
            u'enable_inline_editing_label',
            default=u"Enable inline editing"),
        description=_(
            u'enable_inline_editing_help',
            default=u"Inline Ajax editing requires a fast personal computer and"
            u" a fast browser like Firefox or Safari. You may uncheck this option"
            u" if you use a slow computer or use Internet Explorer 6 or 7."),
        required=False)


class InlineEditOptionManager(object):
    """Our form adapter"""

    implements(IInlineEditOption)
    adapts(ISiteRoot)

    def __init__(self, context):
        """context is supposed to be the Plone site"""

        self.context = context # The Plone site
        membership_tool = getMultiAdapter((context, context.REQUEST), name=u'plone_tools').membership()
        self.member = membership_tool.getAuthenticatedMember()
        return

    @apply
    def enable_inline_editing():

        def get(self):
            return self.member.getProperty('enable_inline_editing')

        def set_(self, value):
            self.member.setProperties(enable_inline_editing=bool(value))
            return

        return property(get, set_)


class InlineEditForm(formbase.EditForm):
    """Our form
    """
    label = _(u'inline_edit_form_label', default=u"Inline edition preferences")
    description = _(u'inline_edit_form_help', default=u"What editing mode do you prefer.")
    form_fields = form.FormFields(IInlineEditOption)

    def __call__(self):
        self.request.set('disable_border', True)
        return super(InlineEditForm, self).__call__()

    @form.action(p_(u'label_save'))
    def handleApply(self, action, data):
        storage = getAdapter(self.context, IInlineEditOption)
        storage.enable_inline_editing = data['enable_inline_editing']
        IStatusMessage(self.request).addStatusMessage(p_(u'Changes made.'), type='info')
        self.request.RESPONSE.redirect(self.request.URL)
        return ''





