============
bda.blogview
============

Overview
========

This package contains a blog-like view. It allows you to use all Archtypes based
content to be viewed as blog entries, as long as they follow the specs of
bda.contentproxy.
  
If commenting is allowed on an object, the comments are displayed as well. The
view provides commenting controls for the displayed objects directly.
 
To make the blogview work, you have to provide an IBlogItemProvider implementing
object.


Example::

 from zope.interface import implements
 from zope.component import getMultiAdapter

 from Acquisition import Explicit

 from Products.CMFPlone.utils import getToolByName

 from bda.blogview.interfaces import IBlogItemProvider
 from bda.blogview.interfaces import IBlogItemIterator
 from bda.blogview.atiterator import ATBlogItemQuery
 
 class BlogItemProvider(Explicit):
    
     implements(IBlogItemProvider)
    
     def __init__(self, context, request):
         self.context = context
         self.request = request
    
     @property
     def items(self):
         putils = getToolByName(self.context.context, 'plone_utils')
         query = ATBlogItemQuery({
             'portal_type': putils.getUserFriendlyTypes(),
             'sort_on': 'modified',
             'sort_order': 'reverse',
         })
         iterator = getMultiAdapter((self.context, query), IBlogItemIterator)
         return [i for i in iterator]


You have to register this implementation as follows::

 <adapter
   for="zope.interface.Interface
        zope.publisher.interfaces.browser.IBrowserRequest"
   provides="bda.blogview.interfaces.IBlogItemProvider"
   factory=".yourmodule.BlogItemProvider"
   name="blog"
  />


Dependencies
============

- plone 3
 
- cornerstone.ui.core
 
- cornerstone.ui.result
 
- bda.contentproxy


Installation
============

1. Make the dependent eggs available in your instance,
  
2. Import extension profiles in your plone instance.


Copyright
=========

Copyright 2008, BlueDynamics Alliance, Austria - 
`www.bluedynamics.com <http://www.bluedynamics.com>`_


Credits
=======

- Written by `Robert Niederreiter <mailto:rnix@squarewave.at>`_
  Squarewave Computing, BlueDynamics Alliance, Austria
        

Licence
=======

- GNU General Public Licence 2.0 or later

