# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import Interface
from zope.interface import Attribute


class IBlogItemProvider(Interface):
    """The Interface to be implemented and registered as multi adapter for
    a context and the request with name 'blog'
    """
    
    def items(self):
        """Return the blog items as catalog brains.
        """


class IBlogItemQuery(Interface):
    """The query definition object for the iterator.
    """


class IBlogItemIterator(Interface):
    """Interface for an Iterator providing Blog Items. 
    """
    
    def __iter__():
        """Iterate through visible Blog Items.
        
        Return catalog brains
        """

