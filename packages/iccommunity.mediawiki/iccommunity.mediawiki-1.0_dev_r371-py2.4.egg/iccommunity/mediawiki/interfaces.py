# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: interfaces.py 297 2008-06-18 20:11:11Z crocha $
#
# end: Platecom header
"""Interfaces
"""

from zope import schema
from zope.interface import Interface

from iccommunity.mediawiki import MediawikiMessageFactory as _

class IRolesPair(Interface):
    """A pair of roles, one from Plone and another from Mediawiki"""
    plone_role = schema.TextLine(title=_(u"Plone Role"))
    mediawiki_role = schema.TextLine(title=_(u"Mediawiki Role"))


class IicCommunityManagementMediawikiRolesMapper(Interface):
    """An interface for a role mapper between Plone and Mediawiki"""
    rolemap = schema.List(title = _(u"Roles Map"),
                                    required = False,
                                    default = [],
                                    description = _(u"Enter a role association "
                                                     "per line using the "
                                                     "format 'Plone Role, "
                                                     "Mediawiki Role' without "
                                                     "quotes."),
                                    value_type=schema.TextLine(title=_(u'Map'),
                                                               required=False))
                                    #value_type=schema.Object(IRolesPair,
                                                              #title=_(u'Map'),
                                                              #required=False))

    def get_parsed_rolemap():
        """Returns a list of pairs containing a string for the Plone
        role and a string for the Mediawiki role.
        """

class IicCommunityManagementMediawikiSQLServer(Interface):
    """An interface for Mediawiki SQL server configuration"""
    hostname = schema.DottedName(title=_(u"Host name"),
                                description=_(u"The database host name"),
				default="localhost",
                                required=True)
				#default=u"localhost")

    username = schema.ASCIILine(title=_(u"User name"),
                                description=_(u"The database user name"),
				default="wikiuser",
                                required=True)

    password = schema.Password(title=_(u"Password"),
                                description=_(u"The database password"),
                                required=True)

    database = schema.ASCIILine(title=_(u"Database name"),
                                description=_(u"The database name"),
				default="wikidb",
                                required=True)

    dbprefix = schema.ASCIILine(title=_(u"Names prefix"),
                                description=_(u"The prefix of table names"),
				default="",
                                required=False)

