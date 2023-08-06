# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import implements
from zope.component import getMultiAdapter

from cornerstone.ui.result.result import ResultBase
from cornerstone.ui.result.batch import NumericBatchVocabBase
from cornerstone.ui.result.slice import NumericBatchedSliceBase

from bda.blogview.interfaces import IBlogItemProvider
from interfaces import IBlogSlice

class BlogResult(ResultBase):
    
    name = 'bda.blogview.blog'
    
    @property
    def results(self):
        provider = getMultiAdapter((self.context, self.request),
                                   IBlogItemProvider,
                                   name=u'blog')
        return provider.items


class BlogBatchVocab(NumericBatchVocabBase):
    
    @property
    def vocab(self):
        return self.generateVocab()


class BlogSlice(NumericBatchedSliceBase):
    
    implements(IBlogSlice)
    
    @property
    def entries(self):
        # XXX
        # needed to find 'reply_come_from' on request in
        # 'entry_threads_snippet.pt'. will be removed until new commenting
        # engine is there.
        self.request['reply_come_from'] = self.context.absolute_url()
        
        slice = self.generateCurrentSlice('blogbatch')
        return [b.getObject() for b in slice]
    
    @property
    def anchor(self):
        return self.request.get('anc', 'undefined')
