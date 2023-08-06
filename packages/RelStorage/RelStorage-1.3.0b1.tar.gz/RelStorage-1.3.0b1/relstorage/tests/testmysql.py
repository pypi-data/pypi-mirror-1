##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Tests of relstorage.adapters.mysql"""

import logging
import unittest

import reltestbase
from relstorage.adapters.mysql import MySQLAdapter


class UseMySQLAdapter:
    def make_adapter(self):
        return MySQLAdapter(
            db='relstoragetest',
            user='relstoragetest',
            passwd='relstoragetest',
            )

class MySQLTests(UseMySQLAdapter, reltestbase.RelStorageTests):
    pass

class MySQLToFile(UseMySQLAdapter, reltestbase.ToFileStorage):
    pass

class FileToMySQL(UseMySQLAdapter, reltestbase.FromFileStorage):
    pass

db_names = {
    'data': 'relstoragetest',
    '1': 'relstoragetest',
    '2': 'relstoragetest2',
    'dest': 'relstoragetest2',
    }

def test_suite():
    suite = unittest.TestSuite()
    for klass in [MySQLTests, MySQLToFile, FileToMySQL]:
        suite.addTest(unittest.makeSuite(klass, "check"))

    try:
        from ZODB.tests.testblob import storage_reusable_suite
    except ImportError:
        # ZODB < 3.9
        pass
    else:
        def create_storage(name, blob_dir):
            from relstorage.relstorage import RelStorage
            adapter = MySQLAdapter(
                db=db_names[name],
                user='relstoragetest',
                passwd='relstoragetest',
                )
            storage = RelStorage(adapter, name=name, create=True,
                blob_dir=blob_dir)
            storage.zap_all()
            return storage

        suite.addTest(storage_reusable_suite(
            'MySQL', create_storage,
            test_blob_storage_recovery=True,
            test_packing=True,
            ))

    return suite

if __name__=='__main__':
    logging.basicConfig()
    unittest.main(defaultTest="test_suite")

