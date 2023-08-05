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

import os

from zope import interface
from zope import schema

from zope.component import zcml

from zope.configuration.exceptions import ConfigurationError
import zope.configuration.fields

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.pagetemplate.interfaces import IPageTemplate
from zope.configuration.fields import GlobalObject

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


from zope.i18nmessageid import MessageFactory
_ = MessageFactory( 'zope' )


class IPluggableTemplatesDirective( interface.Interface ):
    """Parameters for the template directive."""


    for_ = GlobalObject(
            title = _( u'View' ),
            description = _( u'The view for which the template should be used' ),
            required = False,
            default=interface.Interface,
            )

    layer = GlobalObject(
            title = _( u'Layer' ),
            description = _( u'The layer for which the template should be used' ),
            required = False,
            default=IDefaultBrowserLayer,
            )


class IPluggableTemplate( interface.Interface ):

    file = zope.configuration.fields.Path(
            title=_( "Content-generating template." ),
            description=_( "Refers to a file containing a page template (should "
                          "end in extension ``.pt`` or ``.html``)." ),
            required=False,
            )

    name = schema.TextLine(
            title = _( u'Name' ),
            description = _( u"""
                The name to be used.
                Allows named adapter lookups so multiple templates can be assigned to one view.
                """ ),
            required = False,
            default = u'',
            )

    contentType = schema.BytesLine(
        title = _( u'Content Type' ),
        description=_( u'The content type identifies the type of data.' ),
        default='text/html',
        required=False,
        )

    layer = GlobalObject(
            title = _( u'Layer' ),
            description = _( u'The layer for which the template should be used' ),
            required = False,
            default=IDefaultBrowserLayer,
            )

class TemplateFactory( object ):

    def __init__( self, filename, contentType ):
        self.filename = filename
        self.contentType = contentType

    def __call__( self, view, request ):
        template = ViewPageTemplateFile( self.filename,
                                        content_type=self.contentType )
        return template



def templateDirective( _context,
                      file,
                      name,
                      for_=interface.Interface,
                      layer=IDefaultBrowserLayer,
                      contentType='text/html', **kwargs
                      ):
    # Make sure that the template exists
    file = os.path.abspath( str( _context.path( file ) ) )
    if not os.path.isfile( file ):
        raise ConfigurationError( "No such file", file )

    factory = TemplateFactory( file, contentType )

    zcml.adapter( _context, ( factory, ), IPageTemplate, ( for_, layer ), name=name )

class PluggableTemplatesDirective( object ):

    def __init__( self, _context, for_, layer=IDefaultBrowserLayer ):
        self._context = _context
        self.for_ = for_
        self.layer = layer

    def template( self, _context, file, name, contentType='text/html', layer=None, *args, **kw ):
        #import pdb; pdb.set_trace()
        file = os.path.abspath( str( self._context.path( file ) ) )

        if not layer:
            layer = self.layer

        return templateDirective( self._context, file, name, self.for_, layer, contentType )

    def __call__( self ):
        pass
