# -*- coding: utf-8 -*-
# $Id: atkssfields.py 106724 2009-12-16 08:08:32Z glenfant $
"""Overrides rules for KSS inline editing depending on personal preferences"""

from zope.interface import implements
from zope.component import getMultiAdapter
from plone.browserlayer import utils as browserlayer_utils
from archetypes.kss.interfaces import IInlineEditingEnabled
from archetypes.kss.fields import InlineEditingEnabledView as OriginalView
from aws.inlineuserpref.interfaces import IAWSInlineUserPrefLayer

class InlineEditingEnabledView(OriginalView):
    # This adapter overrides the default from archetypes.kss.fields it subclasses.

    __doc__ = OriginalView.__doc__

    implements(IInlineEditingEnabled)

    def __call__(self):
        """See base class
        """
        enabled = super(InlineEditingEnabledView, self).__call__()
        if enabled and IAWSInlineUserPrefLayer in browserlayer_utils.registered_layers():
            # User may deny using inline editing in personal control panel.
            portal_state = getMultiAdapter((self.context, self.request),
                                           name=u'plone_portal_state')
            member = portal_state.member()
            if member:
                enabled = member.getProperty('enable_inline_editing')
        return enabled


