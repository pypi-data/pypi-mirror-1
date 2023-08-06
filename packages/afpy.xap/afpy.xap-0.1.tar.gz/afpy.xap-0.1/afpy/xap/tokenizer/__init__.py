# -*- coding: iso-8859-15 -*-
# Copyright (c) 2006 Nuxeo SAS <http://nuxeo.com>
# Authors : Tarek Ziadé <tziade@nuxeo.com>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id: __init__.py 45713 2006-05-18 13:57:32Z ogrisel $

from afpy.xap.tokenizer.filters import applyFilters
from afpy.xap.tokenizer.filters import AllFilters

def tokenize(data, options=None):
    """ default tokenizer """
    filters = ('splitter', 'stopwords', 'normalizer', 'stemmer')
    return applyFilters(filters, data, options)

