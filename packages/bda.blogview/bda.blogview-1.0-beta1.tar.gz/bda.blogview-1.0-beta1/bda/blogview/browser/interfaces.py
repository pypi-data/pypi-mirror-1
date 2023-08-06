# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import Interface
from zope.interface import Attribute

class IBlogSlice(Interface):
    """The Blog Item Slice Interface.
    """
    
    entries = Attribute(u"The Blog Entries")
    
    anchor = Attribute(u'aA html anchor if existent in url')