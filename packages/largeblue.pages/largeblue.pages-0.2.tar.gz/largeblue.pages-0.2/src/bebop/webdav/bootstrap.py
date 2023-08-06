#!/usr/local/env/python
#############################################################################
# Name:         bootstrap.py
# Purpose:      Ensures utility for the use of WebDAV locking
# Maintainer:   Uwe Oestermeier
# Copyright:    (c) 2007 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################

import transaction
import zope.app.appsetup
from zope.app.appsetup import bootstrap

import zope.locking.interfaces
import zope.locking.utility

def databaseOpenedEventHandler(event):
    """Subscriber to the IDataBaseOpenedEvent

    Create utilities which are required for shortcuts etc.
    """
    db, connection, root, root_folder = bootstrap.getInformationFromEvent(event)
    
    bootstrap.ensureUtility(root_folder,
        zope.locking.interfaces.ITokenUtility,
        'zope.locking.tokens',
        zope.locking.utility.TokenUtility,
        asObject=True)
     
    transaction.commit()
    connection.close()

      

