import os
import sys
import logging

import xapian

from afpy.xap.tokenizer import tokenize
from afpy.xap.settings import DB_FILE
from afpy.xap.model import IndexData, RemoveData, session

def xap_read_write():
    return xapian.flint_open(DB_FILE, xapian.DB_CREATE_OR_OPEN)

def xap_reset():
    return xapian.flint_open(DB_FILE, xapian.DB_CREATE_OR_OVERWRITE)

def xap_read_only():
    return xapian.flint_open(DB_FILE)

def force_reset():
    db = xap_reset()
    del db

from threading import Thread
import time

class IndexationWorker(Thread):
    """reads the SQLDB to do the jobs"""

    def __init__(self, db_file, reset=False):
        Thread.__init__(self)
        self.db_file = db_file
        self.is_working = False
        if not reset:
            self.db = xap_read_write()
        else:
            self.db = xap_reset()
        self.running = False

    def _get_document_internal_id(self, uid):
        """retrieves a document"""
        enquire = xapian.Enquire(self.db)
        query = xapian.Query('Q%s' % uid)
        enquire.set_query(query)
        res = list(enquire.get_mset(0, 1))
        if len(res) == 0:
            return None
        return res[0].docid

    def index_document(self, uid, text, language):
        """indexes the given document"""
        logging.debug('xap:indexing %s' % uid)
        options = {'treshold': 2}
        words = tokenize(text, options=options)
        if language is not None:
            options['lang'] = language
            words.extend(tokenize(text, options=options))

        old_docid = self._get_document_internal_id(uid)
        doc = xapian.Document()
        doc.add_term('Q%s' % uid, 1)
        i = 1
        for word in words:
            doc.add_posting(word, i)
            i += 1

        if old_docid is None:
            self.db.add_document(doc)
        else:
            self.db.replace_document(old_docid, doc)

	logging.debug('xap:%s indexed' % uid)

    def delete_document(self, uid):
        """removes the document"""
        logging.debug('xap:deleting %s' % uid)
        docid = self._get_document_internal_id(uid)
        if docid is not None:
            self.db.delete_document(docid)
        logging.debug('xap:%s deleted' % uid)

    def _get_indexables(self):
        res = session.query(IndexData).all()
        jobs = [(item.docid, item.data, item.language_iso) for item in res]
        if jobs != []:
            logging.debug('xap:reading index table: %s' % str(jobs))
        return jobs

    def _get_removables(self):
        res = session.query(RemoveData).all()
        jobs = [item.docid for item in res]
        if jobs != []:
            logging.debug('xap:reading delete table: %s' % str(jobs))
        return jobs

    def _index_done(self, docid):
        res = session.query(IndexData).filter_by(docid=docid).first()
        session.delete(res)

    def _remove_done(self, docid):
        res = session.query(RemoveData).filter_by(docid=docid).first()
        session.delete(res)
        
    def run(self):
        self.running = True
        logging.debug('xap:launched')
        logging.debug('xap:database has %d documents' % self.db.get_doccount())

        while self.running:
            # index
            self.is_working = True
            indexed = []
            removed = []
            try:
                try:
                    to_index = self._get_indexables()
                    #self.db.begin_transaction()
                    try:
                        for docid, data, language in to_index:
                            self.index_document(docid, data, language=language)
                            indexed.append(docid)
                        # remove
                        to_remove = self._get_removables()
                        for docid in to_remove:
                            self.delete_document(docid)
                            removed.append(docid)
                    except:
                        #self.db.cancel_transaction()
                        raise
                    #else:
                    #    self.db.commit_transaction()
                    #    self.db.flush()

                    # now cleaning sql tables
                    for docid in indexed:
                        self._index_done(docid)

                    for docid in removed:
                        self._remove_done(docid)
                except:
                    raise
            finally:
                self.is_working = False
                session.commit()
                time.sleep(5)
        logging.debug('xap:stopped')

worker = None

def start_server(reset=False):
    global worker
    logging.debug('creating indexation worker over %s' % (DB_FILE))
    worker = IndexationWorker(DB_FILE, reset)
    worker.start()

def stop_server():
    global worker
    if worker is not None:
        worker.running = False
        worker.join()
        worker = None

def is_working():
    return worker.is_working

from atexit import register
register(stop_server)

