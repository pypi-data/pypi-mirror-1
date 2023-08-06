##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Pluggable Authentication Utility implementation

$Id: authentication.py 97982 2009-03-12 13:32:48Z nadako $
"""
import zope.interface
from zope import component
from zope.schema.interfaces import ISourceQueriables
from zope.location.interfaces import ILocation
from zope.site.next import queryNextUtility

from zope.authentication.interfaces import IAuthentication, PrincipalLookupError
import zope.container.btree

from zope.app.authentication import interfaces

class PluggableAuthentication(zope.container.btree.BTreeContainer):

    zope.interface.implements(
        IAuthentication,
        interfaces.IPluggableAuthentication,
        ISourceQueriables)

    authenticatorPlugins = ()
    credentialsPlugins = ()

    def __init__(self, prefix=''):
        super(PluggableAuthentication, self).__init__()
        self.prefix = prefix

    def _plugins(self, names, interface):
        for name in names:
            plugin = self.get(name)
            if not interface.providedBy(plugin):
                plugin = component.queryUtility(interface, name, context=self)
            if plugin is not None:
                yield name, plugin

    def getAuthenticatorPlugins(self):
        return self._plugins(
            self.authenticatorPlugins, interfaces.IAuthenticatorPlugin)

    def getCredentialsPlugins(self):
        return self._plugins(
            self.credentialsPlugins, interfaces.ICredentialsPlugin)

    def authenticate(self, request):
        authenticatorPlugins = [p for n, p in self.getAuthenticatorPlugins()]
        for name, credplugin in self.getCredentialsPlugins():
            credentials = credplugin.extractCredentials(request)
            for authplugin in authenticatorPlugins:
                if authplugin is None:
                    continue
                info = authplugin.authenticateCredentials(credentials)
                if info is None:
                    continue
                info.credentialsPlugin = credplugin
                info.authenticatorPlugin = authplugin
                principal = component.getMultiAdapter((info, request),
                    interfaces.IAuthenticatedPrincipalFactory)(self)
                principal.id = self.prefix + info.id
                return principal
        return None

    def getPrincipal(self, id):
        if not id.startswith(self.prefix):
            next = queryNextUtility(self, IAuthentication)
            if next is None:
                raise PrincipalLookupError(id)
            return next.getPrincipal(id)
        id = id[len(self.prefix):]
        for name, authplugin in self.getAuthenticatorPlugins():
            info = authplugin.principalInfo(id)
            if info is None:
                continue
            info.credentialsPlugin = None
            info.authenticatorPlugin = authplugin
            principal = interfaces.IFoundPrincipalFactory(info)(self)
            principal.id = self.prefix + info.id
            return principal
        next = queryNextUtility(self, IAuthentication)
        if next is not None:
            return next.getPrincipal(self.prefix + id)
        raise PrincipalLookupError(id)

    def getQueriables(self):
        for name, authplugin in self.getAuthenticatorPlugins():
            queriable = component.queryMultiAdapter((authplugin, self),
                interfaces.IQueriableAuthenticator)
            if queriable is not None:
                yield name, queriable

    def unauthenticatedPrincipal(self):
        return None

    def unauthorized(self, id, request):
        challengeProtocol = None

        for name, credplugin in self.getCredentialsPlugins():
            protocol = getattr(credplugin, 'challengeProtocol', None)
            if challengeProtocol is None or protocol == challengeProtocol:
                if credplugin.challenge(request):
                    if protocol is None:
                        return
                    elif challengeProtocol is None:
                        challengeProtocol = protocol

        if challengeProtocol is None:
            next = queryNextUtility(self, IAuthentication)
            if next is not None:
                next.unauthorized(id, request)

    def logout(self, request):
        challengeProtocol = None

        for name, credplugin in self.getCredentialsPlugins():
            protocol = getattr(credplugin, 'challengeProtocol', None)
            if challengeProtocol is None or protocol == challengeProtocol:
                if credplugin.logout(request):
                    if protocol is None:
                        return
                    elif challengeProtocol is None:
                        challengeProtocol = protocol

        if challengeProtocol is None:
            next = queryNextUtility(self, IAuthentication)
            if next is not None:
                next.logout(request)


class QuerySchemaSearchAdapter(object):
    """Performs schema-based principal searches on behalf of a PAU.

    Delegates the search to the adapted authenticator (which also provides
    IQuerySchemaSearch) and prepends the PAU prefix to the resulting principal
    IDs.
    """
    component.adapts(
        interfaces.IQuerySchemaSearch,
        interfaces.IPluggableAuthentication)

    zope.interface.implements(
        interfaces.IQueriableAuthenticator,
        interfaces.IQuerySchemaSearch,
        ILocation)

    def __init__(self, authplugin, pau):
        if (ILocation.providedBy(authplugin) and
            authplugin.__parent__ is not None):
            # Checking explicitly for the parent, because providing ILocation
            # basically means that the object *could* be located. It doesn't
            # say the object must be located.
            self.__parent__ = authplugin.__parent__
            self.__name__ = authplugin.__name__
        else:
            self.__parent__ = pau
            self.__name__ = ""
        self.authplugin = authplugin
        self.pau = pau
        self.schema = authplugin.schema

    def search(self, query, start=None, batch_size=None):
        for id in self.authplugin.search(query, start, batch_size):
            yield self.pau.prefix + id
