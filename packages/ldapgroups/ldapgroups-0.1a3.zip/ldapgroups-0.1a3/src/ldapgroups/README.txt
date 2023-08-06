================
LDAP GroupFolder
================

This is an AuthenticatorPlugin that implements a read-only GroupFolder reflecting the groups
as defined on an LDAP server. It relies on the registration as a named ILDAPAuthentation utility
of an ldappas plugin. It works in tandem with ldappas: ldappas authenticates users, while
ldapgroups looks up their groups and adds the users to the groups 


Setup
-----

	>>> from ldappas.authentication import LDAPAuthentication
	>>> from zope import component
	>>> from ldappas.interfaces import ILDAPAuthentication
	
	>>> users = LDAPAuthentication()
	>>> component.provideUtility(users, ILDAPAuthentication, 'ldap-users')

LDAPAuthentication needs an LDAP adapter, registered as a named ILDAPAdapter utility. 
There's a fake one in the tests module.

	>>> from ldapgroups.tests import FakeLDAPAdapter
	>>> adapter = FakeLDAPAdapter()
	>>> from ldapadapter.interfaces import ILDAPAdapter
	>>> component.provideUtility(adapter, ILDAPAdapter, 'ldap-adapter')

Let's configure the LDAPAuthentication plugin:

	>>> users.adapterName = 'ldap-adapter'
	>>> users.searchBase = 'ou=users,dc=test'
	>>> users.searchScope = 'sub'
	>>> users.loginAttribute = 'cn'
	>>> users.principalIdPrefix = 'ldap.'
	>>> users.titleAttribute = 'sn'

There's no need to fill in the group-related attributes on the LDAPAuthentication plugin,
as LDAPGroups uses its own. For the idAttribute, you should use the attribute that yields 
the Distinguished Name of the user, as LDAP uses this to link users to groups:

	>>> users.idAttribute = 'dn'
	
(For ActiveDirectory, this apparently is 'distinguishedName', so use an LDAP browser to check)
There may be a way around this restriction with advanced queries, but is not (yet?) implemented.

Let's get our LDAP GroupFolder up and running

	>>> from ldapgroups.groupfolder import LDAPGroups
	>>> groups = LDAPGroups('ldap-users', 'group.ldap.')
	>>> groups.groupsSearchBase = 'ou=groups,dc=test'
	>>> groups.groupsSearchScope = 'sub'    
	>>> groups.groupTitleAttribute = 'cn'
	>>> groups.groupIdAttribute = 'dn'
	>>> groups.groupDescriptionAttribute = 'description'
	
Do some registration tests

  >>> groups.getLDAPAuthenticator() == users
  True
  >>> users.getLDAPAdapter() == adapter
  True


Groups can't authenticate

  >>> groups.authenticateCredentials({'login':u'Domain Users','password':'pwd'}) is None
  True

We can lookup groups as principals

  >>> principal = groups.principalInfo(u'group.ldap.cn=Domain Users,ou=groups,dc=test')
  >>> principal
  LDAPGroupInformation(u'group.ldap.cn=Domain Users,ou=groups,dc=test')
  >>> from zope.app.authentication.interfaces import IPrincipalInfo 
  >>> IPrincipalInfo.providedBy(principal)
  True
  
It also provides IReadGroupInformation, which can be used to get the principals

  >>> from ldapgroups.interfaces import IReadGroupInformation
  >>> IReadGroupInformation.providedBy(principal)
  True
  >>> principal.principals
  [u'ldap.cn=Andr\xe9 de Chimpansee,ou=users,dc=test', u'ldap.cn=Louis Kolibri,ou=users,dc=test']



Container behaviour
-------------------

  >>> len(groups)
  2
  >>> groups.keys()
  [u'Administrators', u'Domain Users']
  >>> 'Administrators' in groups
  True
  >>> groups.has_key('Administrators')
  True
  >>> groups.values() 
  [LDAPGroupInformation(u'group.ldap.cn=Administrators,ou=groups,dc=test'), LDAPGroupInformation(u'group.ldap.cn=Domain Users,ou=groups,dc=test')]
  >>> groups.items() == zip(groups.keys(),  groups.values())
  True
  >>> group = groups['Domain Users']
  >>> group
  LDAPGroupInformation(u'group.ldap.cn=Domain Users,ou=groups,dc=test')
  >>> group.description
  u'Users with a domain account'
  >>> group == groups.get('Domain Users')
  True
  >>> groups.get('grupo sportivo') is None
  True
  >>> groups['grupo sportivo'] # doctest: +ELLIPSIS
  Traceback (most recent call last):
    ...
  KeyError


Searching
---------

  >>> groups.search({'cn':'Domain Users'})
  [u'group.ldap.cn=Domain Users,ou=groups,dc=test']
  >>> groups.search({'cn':'Users'})
  []

PAU integration:
----------------

Registers them all to the PAU

  >>> from zope.app.authentication.interfaces import IAuthenticatorPlugin
  >>> component.provideUtility(users, provides=IAuthenticatorPlugin, name='ldap-users')
  >>> component.provideUtility(groups, provides=IAuthenticatorPlugin, name='ldap-groups')

We also need a credentials plugin that will extract the credentials from the
request:

  >>> import zope.interface
  >>> from zope.app.authentication.interfaces import ICredentialsPlugin

  >>> class MyCredentialsPlugin:
  ...
  ...     zope.interface.implements(ICredentialsPlugin)
  ...
  ...     def extractCredentials(self, request):
  ...         return request.get('credentials')
  ...
  ...     def challenge(self, request):
  ...         pass # challenge is a no-op for this plugin
  ...
  ...     def logout(request):
  ...         pass # logout is a no-op for this plugin

  >>> creds = MyCredentialsPlugin()
  >>> component.provideUtility(creds, name='simple-creds')

Register the principalFactory

  >>> import zope.component.event
  >>> from zope.app.authentication import principalfolder
  >>> component.provideAdapter(principalfolder.AuthenticatedPrincipalFactory)
  >>> component.provideAdapter(principalfolder.FoundPrincipalFactory)

We are finally ready to create a pluggable authentication utility and register
the two plugins with it:

  >>> from zope.app import authentication
  >>> pau = authentication.PluggableAuthentication()
  >>> pau['ldap-users'] = users
  >>> pau['ldap-groups'] = groups
  >>> pau['simple-creds'] = creds
  >>> pau.credentialsPlugins = ('simple-creds', )
  >>> pau.authenticatorPlugins = ('ldap-users', 'ldap-groups')
  
Let's authenticate some users

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest(credentials={'login': 'Louis Kolibri', 'password': 'louis2000'})
  >>> louis = pau.authenticate(request)
  >>> louis
  Principal(u'ldap.cn=Louis Kolibri,ou=users,dc=test')

Groups are set by the setGroupsForPrincipal event subscriber

  >>> louis.groups
  []
  >>> class PrincipalCreatedEvent:
  ...     def __init__(self, authentication, principal):
  ...         self.authentication = authentication
  ...         self.principal = principal
  >>> from ldapgroups.groupfolder import setGroupsForPrincipal
  >>> setGroupsForPrincipal(PrincipalCreatedEvent(pau, louis))
  >>> louis.groups
  [u'group.ldap.cn=Domain Users,ou=groups,dc=test']
  >>> component.provideHandler(setGroupsForPrincipal)
  >>> request = TestRequest(credentials={'login': 'Andr\xe9 de Chimpansee', 'password': 'dreten'})
  >>> andre = pau.authenticate(request)
  >>> andre
  Principal(u'ldap.cn=Andr\xe9 de Chimpansee,ou=users,dc=test')
  >>> andre.groups
  [u'group.ldap.cn=Administrators,ou=groups,dc=test', u'group.ldap.cn=Domain Users,ou=groups,dc=test']

  

Browser views
-------------

There's an ISized adapter available for the zmi view.

  >>> from ldapgroups.groupfolder import LDAPGroupSize
  >>> from zope.size.interfaces import ISized
  >>> component.provideAdapter(LDAPGroupSize)
  >>> ISized(group).sizeForSorting()
  ('item', 2)
  
The view's iteminfos function gathers all info about the goups in a groupfolder
  
  >>> from ldapgroups.browser.contents import LDAPGroupFolderContents
  >>> view = LDAPGroupFolderContents(groups, request)
  >>> view.iteminfos()
  [{'url': 'Administrators', 'name': u'Administrators', 'size': u'${items} items'}, {'url': 'Domain%20Users', 'name': u'Domain Users', 'size': u'${items} items'}]