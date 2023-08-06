# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: __init__.py 235 2008-06-10 20:21:40Z crocha $
#
# end: Platecom header
from AccessControl import ModuleSecurityInfo
from zope.i18nmessageid import MessageFactory

MediawikiMessageFactory = MessageFactory('iccommunity.mediawiki')
ModuleSecurityInfo('iccommunity.mediawiki').declarePublic('MediawikiMessageFactory')

GLOBALS = globals()

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
