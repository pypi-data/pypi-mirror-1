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
""" Indexer, takes the work into the SQL DB
"""
import os
import sys
import logging

from afpy.xap.model import session 
from afpy.xap.model import IndexData
from afpy.xap.model import RemoveData

def reset():
    """resets the DBs"""
    session.execute('delete from xap_index_data')
    session.execute('delete from xap_remove_data')

def index_document(docid, data, language=None):
    """puts the data into the table for the indexer to pick it up"""
    logging.debug('sql:indexing %s' % docid)
    
    # check if the document is not already in the index queue
    # if it is the case, we just update its data
    res = session.query(IndexData).filter_by(docid=docid).first()
    if res is None:
        new = IndexData(docid=docid, data=data, language_iso=language)
        session.add(new)
    else:
        res.data = data

    session.commit() # see if we want to let the auto commit work

def delete_document(docid):
    """puts the data into the table for the indexer to remove it"""
    logging.debug('sql:deleting %s' % docid)
    RemoveData.insert().execute(docid=docid)

def work_in_process():
    """retrieve the work in process"""
    index = [doc.docid for doc in IndexData.select().execute()]
    remove = [doc.docid for doc in RemoveData.select().execute()]
    return index, remove

def is_working():
    """checks for the db content"""
    return work_in_process() != ([], [])

