from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from simplon.plone.ldap.engine.interfaces import ILDAPBinding
from simplon.plone.ldap.ploneldap.util import guaranteePluginExists
from simplon.plone.ldap.ploneldap.util import getLDAPPlugin


@adapter(ILDAPBinding, IObjectModifiedEvent)
def HandleModified(config, event):
    if guaranteePluginExists():
        # A new fully configured plugin has been created, so we do not
        # need to do anything anymore.
        return

    luf=getLDAPPlugin()._getLDAPUserFolder()
    luf.manage_edit(
            title="Plone managed LDAP",
            login_attr=config.login_attribute,
            uid_attr=config.userid_attribute,
            rdn_attr=config.rdn_attribute,
            users_base=config.user_base or "",
            users_scope=config.user_scope,
            groups_base=config.group_base or "",
            groups_scope=config.group_scope,
            binduid=config.bind_dn or "",
            bindpwd=config.bind_password or "",
            roles="Member")

