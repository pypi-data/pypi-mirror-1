##############################################################################
#
# Copyright (c) 2001-2004 Zope Corporation and Contributors. All
# Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

# DB stuff copied from testBTrees.py

import sys,os

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ParsedXML')

from Products.ParsedXML import ParsedXML

import glob

from Products.ParsedXML import ParsedXML
from StringIO import StringIO

class PersistenceTestCase(ZopeTestCase.ZopeTestCase):

    implementation = ParsedXML.theDOMImplementation

    def openDB(self):
        from ZODB.FileStorage import FileStorage
        from ZODB.DB import DB
        storage = FileStorage(self.dbName)
        db = DB(storage)
        self.db = db.open().root()

    def closeDB(self):
        get_transaction().commit()
        self.document = None
        self.db._p_jar._db.close()
        self.db = None

    def getAppDocument(self):
        "put the document that startup put in the db in self.document"
        self.document = self.db['doc']

    def cycleDB(self):
        """close and open the db and replace self.document.
        Any nonpersistent changes to self.document should be lost."""
        self.closeDB()
        self.openDB()
        self.getAppDocument()

    def delDB(self):
        map(os.unlink, glob.glob("fs_tmp__*"))

    def afterSetUp(self):
        """open db, create a document in the db, set self.document to it"""

        self.dbName = 'fs_tmp__%s' % os.getpid()
        self.openDB()
        self.db['doc'] = ParsedXML.ParsedXML('foo')
        get_transaction().commit()
        self.document = self.db['doc']

    def beforeTearDown(self):
        self.closeDB()
        self.delDB()

    def testIDPersistence(self):
        "assert that changing the ID persists over transactions"
        self.document._setId('newId')
        self.cycleDB()
        assert self.document.getId() == 'newId'

    def testParsedXMLDOMPersistence(self):
        "assert that a Parsed XML DOM edit persists over transactions"
        elt = self.document.createElement('elt')
        self.document.firstChild.appendChild(elt)
        self.cycleDB()
        childLen = self.document.firstChild.childNodes.length
        assert childLen == 1, "DOM edit didn't persist"

    def testDOMPersistence(self):
        "assert that a DOM edit persists over transactions"

        doc = ParsedXML.createDOMDocument()

        import OFS.SimpleItem
        si = self.db['si'] = OFS.SimpleItem.SimpleItem()
        si.doc = doc
        elt = si.doc.createElement('elt')
        si.doc.firstChild.appendChild(elt)

        self.cycleDB()
        # not using the normal db document, must grab ourselves
        si = self.db['si']
                
        childLen = si.doc.firstChild.childNodes.length
        assert childLen == 1, "DOM edit didn't persist"
        
    def testParsePersistence(self):
        "assert that a parse persists over transactions"
        testDir = os.path.join(
            sys.modules['Products.ParsedXML'].__path__[0],
            'tests')
        filename = os.path.join(testDir, 'xml', '4ohn4ktj.xml')
        file = open(filename)
        self.document.parseXML(filename)
        file.close()
        childLen = self.document.firstChild.childNodes.length
        self.cycleDB()
        childLen1 = self.document.firstChild.childNodes.length
        assert childLen == childLen1, "parse didn't persist"

    def testSubnodeParsePersistence(self):
        "assert that a subnode parse persists over transactions"        
        docString = '<?xml version="1.0" ?><foo></foo>'
        subNodeString = '<foo>bar</foo>'
        self.document.documentElement.parseXML(StringIO(subNodeString))
        self.cycleDB()
        childLen = self.document.documentElement.childNodes.length
        assert childLen == 1, "parse on subnode didn't persist"

    # right now it's too annoying to get parsing to work at a transient
    # document proxy, but it could be less aggravating if we had a better
    # way to get at the persistent document.
    #def checkTransientDocumentParsePersistence(self):
    #    """assert that a parse of a transient proxy of the document
    #    persists over transactions"""
    #    docStringBefore = '<?xml version="1.0" ?><foo></foo>'
    #    docStringAfter = '<?xml version="1.0" ?><foo>bar</foo>'
    #    self.document.documentElement.ownerDocument.parseXML(
    #        StringIO(docStringAfter))
    #    self.cycleDB()
    #    childLen = self.document.documentElement.childNodes.length
    #    assert childLen == 1, "parse on subnode didn't persist"

#      def checkTheseDamnTests(self):
#          "assert that I understand how these tests should work"
#          docString = '<?xml version="1.0" ?><foo>fff</foo>'        
#          self.document.parseXML(StringIO(docString))
#          get_transaction().commit()
#          # db and doc length now 1
#          self.document.documentElement.removeChild(
#              self.document.documentElement.firstChild)
#          # doc length 0, db length 1
        
#          # do what closeDB and openDB do, but *don't commit*
#          # so the above edit shouldn't stay.

#          #closeDB but don't commit
#          #get_transaction().commit()
#          self.document = None
#          self.db._p_jar._db.close()
#          self.db = None

#          #openDB
#          from ZODB.FileStorage import FileStorage
#          from ZODB.DB import DB
#          storage = FileStorage(self.dbName)
#          db = DB(storage)
#          self.db = db.open().root()

#          self.getAppDocument()
#          get_transaction().commit()
#          assert self.document.documentElement.childNodes.length == 1, (
#              "these tests are faulty")


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(PersistenceTestCase))
        return suite
