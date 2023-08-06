# Copyright 2008-2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# GNU General Public Licence Version 2 or later

import ldap
from base import LDAPConnector
from base import LDAPCommunicator
from base import testLDAPConnectivity

class LDAPSession(object):
    
    def __init__(self, serverProps, cache=None):
        """XXX cache kwarg is deprecated and will be removed in version 1.4.
        """
        if cache is None:
            cache = serverProps.cache
        connector = LDAPConnector(serverProps.server,
                                  serverProps.port,
                                  serverProps.user,
                                  serverProps.password,
                                  cache)
        self.communicator = LDAPCommunicator(connector)
    
    def checkServerProperties(self):
        """ Test if connection can be established.
        """
        res = testLDAPConnectivity(\
                self.communicator._connector.server,
                self.communicator._connector.port)
        if res == 'success':
            return (True, 'OK')
        else:
            return (False, res)
    
    def setBaseDN(self, baseDN):
        """Set the base DN you want to work on.
        """
        self.communicator.setBaseDN(baseDN)
    
    def search(self, queryFilter, scope, baseDN=None,
               force_reload=False, attrlist=None, attrsonly=0):
        """Search the directory.
        
        Look at bda.ldap.base.LDAPCommunicator.search() for details.
        """
        func = self.communicator.search
        return self._perform(func, queryFilter, scope, baseDN,
                             force_reload, attrlist, attrsonly)
    
    def add(self, dn, data):
        """Insert an entry into directory.
        
        Look at bda.ldap.base.LDAPCommunicator.add() for details.
        """
        func = self.communicator.add
        return self._perform(func, dn, data)
    
    def modify(self, dn, data, replace=False):
        """Modify an existing entry in the directory.
        
        @param dn: Modification DN
        @param data: either list of 3 tuples (look at
                     bda.ldap.base.LDAPCommunicator.modify for details), or
                     a dictionary representing the entry or parts of the entry.
        @param replace: if set to True, replace entry at DN entirely with data.
        
        XXX: implement described behaviour for data
        """
        func = self.communicator.modify
        return self._perform(func, dn, data)
    
    def delete(self, dn):
        """Delete an entry from the directory.
        
        Take the DN to delete from the directory as argument.
        """
        func = self.communicator.delete
        return self._perform(func, dn)
    
    def _perform(self, function, *args, **kwargs):
        """Try to perform the given function with the given argument.
        
        If LDAP directory is down, bind again and retry given function.
        
        XXX: * Improve retry logic in LDAPSession 
             * Extend LDAPSession object to handle Fallback server(s)
        """
        if self.communicator._con is None:
            self.communicator.bind()
        try:
            return function(*args, **kwargs)
        except ldap.SERVER_DOWN:
            self.communicator.bind()
            return function(*args, **kwargs)