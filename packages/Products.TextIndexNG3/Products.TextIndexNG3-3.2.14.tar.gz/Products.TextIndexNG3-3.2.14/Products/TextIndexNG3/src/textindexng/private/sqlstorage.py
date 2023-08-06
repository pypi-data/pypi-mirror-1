###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
Storage of docid -> wordids mapping

$Id: sqlstorage.py 1116 2005-05-06 15:09:01Z ajung $
"""

from pysqlite2 import dbapi2 as sqlite
from zope.interface import implements
from zope.component.interfaces import IFactory
from Persistence import Persistent
from BTrees.IOBTree import IOBTree
import BTrees.Length 

import time
from textindexng.interfaces import IStorage
from Products.ZCTextIndex.WidCode import encode, decode
from docidlist import DocidList

class StorageException(Exception):  pass

class SQLStorage(Persistent):
    """ storage to keep the mapping wordId to sequence
        of document ids and vis-versa.
    """

    implements(IStorage)

    def __init__(self): 
        self.clear()

    def clear(self):
        self.db = sqlite.connect('shell.db')
        self.cursor = self.db.cursor()
        self.cursor.execute('create table storage(docid int, wordid int)')
        self.cursor.execute('create index docid_idx on storage(docid)')
        self.cursor.execute('create index wordid_idx on storage(wordid)')
        self._length = BTrees.Length.Length()
    
    def __len__(self): return self._length()
    numberDocuments = __len__

    def insertDocument(self, docid, widlist):
        print '+'*80
        ts = time.time()
        tp = [(docid, wid) for wid in widlist]
        print time.time()-ts
        ts = time.time()
        self.cursor.executemany('insert into storage (docid, wordid) values(?,?)', tp)
        print time.time()-ts

#        self.db.commit()

    def removeDocument(self, docid):

        try:
            wordids = self._doc2wid[docid]
        except KeyError:
            return # silently ignore 

        tree = self._wid2doc
        tree_has = tree.has_key
        for wordid in decode(wordids):

            if tree_has(wordid):
                try:
                    tree[wordid].remove(docid)
                except KeyError:
                    pass

                if not tree[wordid]:
                    del tree[wordid]

        del self._doc2wid[docid]
        self._length.change(-1)

    def getDocIds(self):
        return self._doc2wid.keys()

    def getDocumentsForWordId(self, wordid):
        try:
            return self._wid2doc[wordid]
        except (TypeError, KeyError):
            return DocidList()

    def getDocumentsForWordIds(self, wordidlist):
        
        r = DocidList()
        for wordid in wordidlist:
            try:
                docids = self._wid2doc[wordid]
            except (TypeError, KeyError):
                continue

            r = r.union(docids)
        return r

    def getWordIdsForDocId(self, docid):
        try:
            return decode(self._doc2wid[docid])
        except KeyError:
            raise StorageException('No such docid: %d' % docid)

    def hasContigousWordids(self, docid, wordids):
        # The trick of perform a phrase search is to use the feature
        # that the string encoded wids can be search through string.find()
        encoded_wids = encode(wordids)
        encoded_document = self._doc2wid[docid]
        return encoded_wids in encoded_document

class SQLStorageFactory:
    
    implements(IFactory)

    def __call__(self):
        return SQLStorage()

    def getInterfaces(self):
        return implementedBy(SQLStorage)

SQLStorageFactory = SQLStorageFactory()
