from zope.component import adapter
from simplon.plone.ldap.engine.interfaces import ILDAPProperty
from simplon.plone.ldap.ploneldap.util import guaranteePluginExists
from simplon.plone.ldap.ploneldap.util import getLDAPPlugin
from simplon.plone.ldap.ploneldap.util import configureLDAPSchema
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.app.container.interfaces import IObjectRemovedEvent

@adapter(ILDAPProperty, IObjectCreatedEvent)
def HandleCreated(property, event):
    if guaranteePluginExists():
        # A new fully configured plugin has been created, so we do not
        # need to do anything anymore.
        return

    luf=getLDAPPlugin()._getLDAPUserFolder()
    luf.manage_addLDAPSchemaItem(
            ldap_name=property.ldap_name,
            friendly_name=property.description,
            public_name=property.plone_name,
            multivalued=property.multi_valued)


@adapter(ILDAPProperty, IObjectModifiedEvent)
def HandleModified(property, event):
    if guaranteePluginExists():
        # A new fully configured plugin has been created, so we do not
        # need to do anything anymore.
        return

    configureLDAPSchema()


@adapter(ILDAPProperty, IObjectRemovedEvent)
def HandleRemoved(property, event):
    if guaranteePluginExists():
        # A new fully configured plugin has been created, so we do not
        # need to do anything anymore.
        return

    luf=getLDAPPlugin()._getLDAPUserFolder()
    luf.manage_deleteLDAPSchemaItems([property.ldap_name])

