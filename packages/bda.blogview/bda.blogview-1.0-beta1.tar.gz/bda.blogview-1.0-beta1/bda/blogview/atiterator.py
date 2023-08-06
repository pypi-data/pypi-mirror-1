# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import implements

from Products.CMFPlone.utils import getToolByName

from interfaces import IBlogItemQuery
from interfaces import IBlogItemIterator


class ATBlogItemQuery(object):
    """Blog Item query implemetation for archetypes using the portal catalog.
    """
    
    implements(IBlogItemQuery)
    
    def __init__(self, query):
        self.query = query


class ATBlogItemIterator(object):
    """Blog Item iterator for archetypes.
    """
    
    implements(IBlogItemIterator)
    
    def __init__(self, context, query):
        self.context = context
        self.query = query
    
    def __iter__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        for item in catalog(self.query.query):
            yield item
