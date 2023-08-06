# -*- coding: utf-8 -*-
# $Id: __init__.py 106618 2009-12-13 23:35:52Z glenfant $
"""aws.inlineuserpref package"""

from AccessControl import ModuleSecurityInfo
from zope.i18nmessageid import MessageFactory

AWSInlineUserPrefMessageFactory = MessageFactory('aws.inlineuserpref')
ModuleSecurityInfo('aws.inlineuserpref').declarePublic('AWSInlineUserPrefMessageFactory')
