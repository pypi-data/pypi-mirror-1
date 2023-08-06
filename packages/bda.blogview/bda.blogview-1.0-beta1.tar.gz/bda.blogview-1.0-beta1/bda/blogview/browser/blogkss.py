# -*- coding: utf-8 -*-
#
# Copyright 2008, BDA - Blue Dynamics Alliance, Austria - www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.component import getMultiAdapter

from kss.core import KSSView
from kss.core import kssaction

class BlogViewKSS(KSSView):
    
    @kssaction
    def renderBlogView(self):
        view = getMultiAdapter((self.context, self.request),
                               name=u'blogkssview')
        view = view.__of__(self.context)
        ksscore = self.getCommandSet('core')
        ksscore.replaceHTML('#cornerstone_result_bda_blogview_blog', view())
