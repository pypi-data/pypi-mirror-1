#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2007 Tarek Ziadé
#
# Authors:
#   Tarek Ziadé <tarek@ziade.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
""" Searcher
"""

import os
import logging

import xapian

from afpy.xap.tokenizer import tokenize
from afpy.xap.settings import DB_FILE
from afpy.xap.model import Statistics, session

def read_only():
    return xapian.flint_open(DB_FILE)

def corpus_size():
    """retrieves number of docs"""
    db = read_only()
    return db.get_doccount()

def _get_document_internal_id(uid):
    """retrieves a document"""
    enquire = xapian.Enquire(read_only())
    query = xapian.Query('Q%s' % uid)
    enquire.set_query(query)
    res = list(enquire.get_mset(0, 1))
    if len(res) == 0:
        return None
    return res[0].docid

def document_exists(uid):
    """tels if the document exists"""
    return _get_document_internal_id(uid) is not None

def document_terms(uid):
    """retrieves terms"""
    db = read_only()
    docid = _get_document_internal_id(uid)
    if docid is not None:
        return (el.term for el in read_only().get_document(docid).termlist()
                if el.term != 'Q%s' % uid)
    return None

def search(query, or_=False, language=None):
    """search"""
    logging.debug('searching for "%s"' % query)

    db = read_only()
    options = {'treshold': 2}
    if language is not None:
        options['lang'] = language

    tquery = tokenize(query, options=options)
    enquire = xapian.Enquire(db)
    if or_:
        op = xapian.Query.OP_OR
    else:
        op = xapian.Query.OP_AND

    xquery = xapian.Query(op, tquery)
    enquire.set_query(xquery)
    res = enquire.get_mset(0, 100)

    def _extract_uid(result):
        # buuuu
        ids = [t.term for t in result.document.termlist()
              if t.term.startswith('Q')]
        if len(ids) > 0:
            return ids[0][1:]
        return None

    logging.debug('searching for "%s" is over' % query)

    #stat = session.query(Statistics).filter_by(query=query).first()
    #if stat is not None:
    #    stat.count = stat.count + 1
    #else:
    #    session.add(Statistics(query=query, count=1))

    return (_extract_uid(el) for el in res)


