# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 STX Next Sp. z o.o. and Contributors.
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

import sys, cStringIO, os.path
import cPickle

def get_database_path():
    """
    Guess ZODB database file path.
    """
    ## instance created using 'mkzopeinstance.py'
    path = os.path.join(INSTANCE_HOME, 'var', 'Data.fs')
    if os.path.isfile(path):
        return path
        
    ## instance created using 'buildout'
    path = os.path.join(CLIENT_HOME, '..', 'filestorage', 'Data.fs')
    if os.path.isfile(path):
        return path
    
    return None

def zodb_analyze(path=None):
    """
    Analyze ZODB database.
    @author: Wojciech Lichota
    """
    try:
        from ZODB.scripts import analyze
    except ImportError:
        print 'ZODB.scripts.analyze not found!'
        return
    
    if not path:
        path = get_database_path()
    
    ## because analyze.analyze prints lot of error message, we redairect it to /dev/null
    try:
        null = open('/dev/null', 'w')
    except IOError:
        ## not in unix/linux
        null = cStringIO.StringIO()
    
    stdout, stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = null, null
        
    result = analyze.analyze(path)
    
    sys.stdout, sys.stderr = stdout, stderr
    
    analyze.report(result)

def get_transactions(path=None):
    """
    Iterate through ZODB's transactions. 
    """
    try:
        from ZODB.FileStorage import FileIterator
    except ImportError:
        print 'ZODB tools not found!'
        return

    if not path:
        path = get_database_path()

    return FileIterator(path)
    
def transactions_log(path=None):
    """
    Iterate through ZODB's transactions - return nice formated transcation log.
    """
    try:
        from ZODB.utils import u64
        from ZODB.TimeStamp import TimeStamp
    except ImportError:
        print 'ZODB tools not found!'
        return

    log_line = "Trans #%05d tid=%016x time=%s status=%r user=%r description=%r size=%d"

    iter = get_transactions(path)
    for i, trans in enumerate(iter):
        size = sum([len(record.data) for record in trans])
        line_data = (i, u64(trans.tid), TimeStamp(trans.tid), trans.status, trans.user, trans.description, size)
        yield log_line % line_data
    
    iter.close()
    
def unpickle_transaction(trans):
    """
    Unickle all transaction records.
    """
    return [cPickle.loads(record.data) for record in trans]
