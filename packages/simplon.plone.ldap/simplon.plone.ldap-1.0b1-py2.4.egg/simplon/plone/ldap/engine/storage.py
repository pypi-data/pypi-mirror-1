from Persistence import Persistent
from zope.interface import implements
from zope.app.container.ordered import OrderedContainer
from zope.app.container.interfaces import INameChooser
from simplon.plone.ldap.engine.interfaces import ILDAPServerStorage
from simplon.plone.ldap.engine.interfaces import ILDAPSchema
from simplon.plone.ldap.engine.interfaces import ILDAPConfiguration
from BTrees.OOBTree import OOBTree
from ldap import SCOPE_SUBTREE
from simplon.plone.ldap.engine.schema import LDAPProperty


class LDAPConfiguration(Persistent):
    implements(ILDAPConfiguration)

    ldap_type = u"LDAP"
    rdn_attribute = u"uid"
    userid_attribute = u"uid"
    login_attribute = u"uid"

    bind_dn = u""
    bind_password = u""
    user_base = u""
    user_scope = SCOPE_SUBTREE
    group_base = u""
    group_scope = SCOPE_SUBTREE

    def __init__(self):
        self.servers=LDAPServerStorage()
        self.schema=LDAPSchema()

        self.schema.addItem(LDAPProperty(
            ldap_name=u"uid", description=u"User id"))
        self.schema.addItem(LDAPProperty(
            ldap_name=u"mail", plone_name=u"email",
            description=u"Email address"))
        self.schema.addItem(LDAPProperty(
            ldap_name=u"cn", plone_name=u"fullname",
            description=u"Canonical Name"))



class LDAPContainer(OrderedContainer):
    """Base class for our containers.
    """
    def __init__(self):
        OrderedContainer.__init__(self)
        self._data=OOBTree()

    def addItem(self, item):
        chooser=INameChooser(self)
        self[chooser.chooseName(None, item)]=item


class LDAPServerStorage(LDAPContainer):
    """A container for LDAP servers.
    """
    implements(ILDAPServerStorage)



class LDAPSchema(LDAPContainer):
    """A container for LDAP properties.
    """
    implements(ILDAPSchema)


