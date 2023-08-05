from zope.interface import Interface
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Container
from zope.schema import Int
from zope.schema import Password
from zope.schema import TextLine

from zope.app.container.interfaces import IContained
from zope.app.container.interfaces import IOrderedContainer
from zope.app.container.interfaces import IContainerNamesContainer
from zope.app.container.constraints import contains

from Products.CMFPlone import PloneMessageFactory as _

from ldap import SCOPE_SUBTREE

class ILDAPBinding(Interface):
    ldap_type = Choice(
            title=_(u"label_ldap_type",
                default=u"LDAP server type"),
            description=_(u"help_ldap_server_type",
                default=u"Plone supports both Active Directory and standard "
                        u"LDAP servers. For Active Directory the read-only "
                        u"LDAP interface which is enabled for all Active "
                        u"Directory servers can be used."),
            vocabulary="simplon.plone.ldap.engine.LDAPServerTypes",
            default=u"LDAP",
            required=True)

    rdn_attribute = Choice(
            title=_(u"label_ldap_dn_attribute",
                default=u"rDN attribute"),
            description=_(u"help_ldap_dn_attribute",
                default=u"This is attribute is used to build the "
                        u"distinguished name (DN) for users that are being "
                        u"created in your LDAP directory. This is commonly "
                        u"either the users full name ('cn' property) or the "
                        u"userid ('uid' property)."),
            default=u"uid",
            vocabulary="simplon.plone.ldap.engine.LDAPSingleValueAttributes",
            required=True)

    userid_attribute = Choice(
            title=_(u"label_ldap_userid_attribute",
                default=u"user id attribute"),
            description=_(u"help_ldap_userid_attribute",
                default=u"This attribute is used as the userid inside Plone "
                        u"for LDAP users. It has to be unique for all users."),
            default=u"uid",
            vocabulary="simplon.plone.ldap.engine.LDAPSingleValueAttributes",
            required=True)

    login_attribute = Choice(
            title=_(u"label_ldap_login_attribute",
                default=u"login name attribute"),
            description=_(u"help_ldap_login_attribute",
                default=u"The attribute is used as the login name for LDAP "
                        u"users logging into your site. In most cases this "
                        u"should be the same as the user id attribute."),
            default=u"uid",
            vocabulary="simplon.plone.ldap.engine.LDAPSingleValueAttributes",
            required=True)

    bind_dn = TextLine(
            title=_(u"label_ldap_bind_dn",
                default=u"Bind DN"),
            description=_(u"help_ldap_bind_dn",
                u"The DN of a manager account in the LDAP directory. This "
                u"must be allowed to access all user and group information "
                u"as well as be able to update and create users and groups. "
                u"Please note that Plone only supports simple binds. SASL "
                u"is not supported."),
            required=False)

    bind_password = Password(
            title=_(u"label_ldap_bind_password",
                default=u"Bind password"),
            description=_(u"help_ldap_bind_password",
                u"Password to use when binding to the LDAP server."),
            required=False)

    user_base = TextLine(
            title=_(u"label_ldap_user_base",
                default=u"Base DN for users"),
            description=_(u"help_ldap_user_base",
                default=u"This is the location in your LDAP directory where "
                        u"all users are stored."),
            required=True)

    user_scope = Choice(
            title=_(u"label_ldap_user_scope",
                default=u"Search scope for users"),
            description=_(u"help_ldap_user_scope",
                default=u"The search scope determines where the LDAP server "
                        u"will search for users. With BASE it will only look "
                        u"for users who directly in the user base location. "
                        u"SUBTREE will allow the server to also look in "
                        u"subfolders of the user base location"),
            default=SCOPE_SUBTREE,
            vocabulary="simplon.plone.ldap.engine.LDAPScopes",
            required=True)

    group_base = TextLine(
            title=_(u"label_ldap_group_base",
                default=u"Base DN for groups"),
            description=_(u"help_ldap_group_base",
                default=u"This is the location in your LDAP directory where "
                        u"all groups are stored."),
            required=True)

    group_scope = Choice(
            title=_(u"label_ldap_group_scope",
                default=u"Search scope for groups"),
            description=_(u"help_ldap_group_scope",
                default=u"The search scope determines where the LDAP server "
                        u"will search for groups. With BASE it will only look "
                        u"for users who directly in the group base location. "
                        u"SUBTREE will allow the server to also look in "
                        u"subfolders of the group base location"),
            default=SCOPE_SUBTREE,
            vocabulary="simplon.plone.ldap.engine.LDAPScopes",
            required=True)


class ILDAPConfiguration(ILDAPBinding):
    """LDAP configuration utility"""

    servers = Container(title=u"LDAP servers",
            description=u"List of LDAP servers that can be used.",
            required=True)

    schema = Container(title=u"LDAP schema",
            description=u"The LDAP schema contains information on used LDAP properties",
            required=True)


class ILDAPServerStorage(IOrderedContainer, IContainerNamesContainer):
    """A storage for rules.
    """

    contains("simplon.plone.ldap.engine.interfaces.ILDAPServer")


class ILDAPServerConfiguration(Interface):
    """Configuration of an LDAP server.
    """
    enabled = Bool(
            title=_(u"label_ldap_enabled",
                default=u"Enabled"),
            description=_(u"help_ldap_enabled",
                default=u"Use this LDAP server"),
            default=False,
            required=True)

    server = TextLine(
            title=_(u"label_ldap_server",
                default=u"LDAP server"),
            description=_(u"help_ldap_server",
                default="The address or hostname of the LDAP server."),
            default=u"localhost",
            required=True)

    connection_type = Choice(
            title=_(u"label_ldap_connection_type",
                default=u"LDAP connection type"),
            description=_(u"help_ldap_connection_type",
                default=u""),
            vocabulary="simplon.plone.ldap.engine.LDAPConnectionTypes",
            default=0,
            required=True)

    connection_timeout = Int(
            title=_(u"label_connection_timeout",
                default=u"Connection timeout"),
            description=_(u"help_connection_timeout",
                default=u"The timeout in seconds to wait for a connection to "
                "the LDAP server to be established."),
            default=5,
            min=-1,
            max=300,
            required=True)

    operation_timeout = Int(
            title=_(u"label_operation_timeout",
                default=u"Operation timeout"),
            description=_(u"help_operation_timeout",
                default=u"The timeout in seconds to wait for an operation such "
                "as a search or update to complete. If no timeout should be "
                "used use -1 as value."),
            default=-1,
            min=-1,
            max=300,
            required=True)


class ILDAPServer(IContained, ILDAPServerConfiguration):
    """A LDAP server
    """


class ILDAPSchema(IOrderedContainer, IContainerNamesContainer):
    """A storage for an LDAP schema.
    """

    contains("simplon.plone.ldap.engine.interfaces.ILDAPProperty")


class ILDAPPropertyConfiguration(Interface):
    description = TextLine(
            title=_(u"label_property_description",
                default=u"Property description"),
            required=False)

    ldap_name = TextLine(
            title=_(u"label_ldap_property",
                default=u"LDAP property name"),
            description=_(u"help_ldap_property",
                default=u"The name of the property as used in the "
                "LDAP directory."),
            required=True)

    plone_name = TextLine(
            title=_(u"label_plone_property",
                default= u"Plone property name"),
            description=_(u"help_plone_property",
                default=u"The name of the property as used in the Plone site. "
                        u"If no name is specified the property will not be "
                        u"visible in Plone but still be used as login name, "
                        u"user id or rDN."),
            required=False)

    multi_valued  = Bool(
            title=_(u"label_multi_valued",
                default=u"Multi-valued property"),
            description=_(u"help_multi_valued",
                default=u"Select if this property can have multiple values."),
            required=True)


class ILDAPProperty(IContained, ILDAPPropertyConfiguration):
    """A LDAP property
    """

