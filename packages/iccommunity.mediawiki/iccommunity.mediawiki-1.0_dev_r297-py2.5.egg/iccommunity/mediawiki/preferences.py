# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: preferences.py 297 2008-06-18 20:11:11Z crocha $
#
# end: Platecom header
from string import strip

from Acquisition import aq_inner
from persistent import Persistent
from zope.interface import implements
from zope.component import getUtility
from OFS.SimpleItem import SimpleItem
from zope.schema.fieldproperty import FieldProperty

import interfaces

#class RolesPair:
    #implements(interfaces.IRolesPair)

    #def __init__(self, plone_role='', mediawiki_role=''):
        #import pdb; pdb.set_trace()
        #self.plone_role = plone_role
        #self.mediawiki_role = mediawiki_role


class icCommunityManagementMediawikiRolesMapper(SimpleItem):
    implements(interfaces.IicCommunityManagementMediawikiRolesMapper)

    rolemap = FieldProperty(interfaces.IicCommunityManagementMediawikiRolesMapper['rolemap'])

    def get_parsed_rolemap(self):
        """Returns a list of pairs containing a string for the Plone
        role and a string for the Mediawiki role.
        """

        pairs = []
        for item in self.rolemap:
            if item is not None:
                pairs += [tuple(map(strip, item.split(';')))]

        return pairs


def mediawiki_roles_form_adapter(context):
    return getUtility(interfaces.IicCommunityManagementMediawikiRolesMapper,
                      name='iccommunity.configuration',
                      context=context)


class icCommunityManagementMediawikiSQLServer(SimpleItem):
    implements(interfaces.IicCommunityManagementMediawikiSQLServer)

    hostname = FieldProperty(interfaces.IicCommunityManagementMediawikiSQLServer['hostname'])
    username = FieldProperty(interfaces.IicCommunityManagementMediawikiSQLServer['username'])
    password = FieldProperty(interfaces.IicCommunityManagementMediawikiSQLServer['password'])
    database = FieldProperty(interfaces.IicCommunityManagementMediawikiSQLServer['database'])
    dbprefix = FieldProperty(interfaces.IicCommunityManagementMediawikiSQLServer['dbprefix'])


def mediawiki_sql_server_adapter(context):
    return getUtility(interfaces.IicCommunityManagementMediawikiSQLServer,
                      name='iccommunity.configuration',
                      context=context)

