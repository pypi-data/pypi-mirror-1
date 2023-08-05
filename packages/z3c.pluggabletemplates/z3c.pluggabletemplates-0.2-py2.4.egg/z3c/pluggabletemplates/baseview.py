##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "reStructuredText"

from zope import interface
from zope import component

from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.browser import BrowserView

from interfaces import ITemplatedContentProvider


class TemplatedContentProvider( object ):
    interface.implements( ITemplatedContentProvider )

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def update(self):
        pass

    def render(self):
        return self.template()

class BaseView( TemplatedContentProvider, BrowserView ):

    def __call__(self):
        self.update()
        return self.render()

class MasterTemplatedContentProvider( TemplatedContentProvider ):


    def render(self):
        return self.master()




class MasterView( MasterTemplatedContentProvider, BrowserView ):

    def __call__(self):
        self.update()
        return self.render()
