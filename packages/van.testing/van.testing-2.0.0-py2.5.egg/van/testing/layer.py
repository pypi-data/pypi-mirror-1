##############################################################################
#
# Copyright (c) 2008 Vanguardistas LLC.
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
from zope.configuration import xmlconfig
from zope.app.component import hooks # BBB: import from zope.site at a later date
from zope.testing.cleanup import cleanUp
import wsgi_intercept

def null_layer(layer):
    """Sets up a class as a layer that doesn nothing.

    Useful if you want a layer to inherit from other layers but not inherit
    their methods. Inheriting the method can cause it to be triggered twice as
    the zope testrunner (zope.testing) walks the super-classes of the layer
    firing the setup methods.

        >>> class LayerA:
        ...     @classmethod
        ...     def setUp(cls):
        ...         print 'fired'
        ...     @classmethod
        ...     def tearDown(cls):
        ...         print 'fired'
        ...     @classmethod
        ...     def testTearDown(cls):
        ...         print 'fired'
        ...     @classmethod
        ...     def testSetUp(cls):
        ...         print 'fired'

    If we just subclass the method, then our subclass will inherit the methods:

        >>> class LayerB(LayerA):
        ...     pass
        >>> LayerB.setUp()
        fired
        >>> LayerB.tearDown()
        fired
        >>> LayerB.testSetUp()
        fired
        >>> LayerB.testTearDown()
        fired

    So, we override

        >>> null_layer(LayerB)
        >>> LayerB.setUp()
        >>> LayerB.tearDown()
        >>> LayerB.testSetUp()
        >>> LayerB.testTearDown()
    """
    def null(cls):
        pass
    layer.setUp = classmethod(null)
    layer.tearDown = layer.setUp
    layer.testSetUp = layer.setUp
    layer.testTearDown = layer.setUp


def zcml_layer(layer):
    """Sets up a class as a ZCMLLayer.

    The class can have 2 attributes:
        zcml: The site zcml file to load.
        allow_teardown: Whether to allow teardown of this layer.
                        Default: True
    """

    def setUp(cls):
        hooks.setHooks()
        context = xmlconfig.file(cls.zcml)
    layer.setUp = classmethod(setUp)

    def tearDown(cls):
        cleanUp()
        if not getattr(cls, 'allow_teardown', True):
            raise NotImplementedError
    layer.tearDown = classmethod(tearDown)

    def null(cls):
        pass
    layer.testSetUp = classmethod(null)
    layer.testTearDown = classmethod(null)


class ErrorHandler:
    """This middleware sets up the environ so that handleErrors actually works.

    zope.testbrowser.Browser.handleErrors that is.
    """
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        if environ.get('HTTP_X_ZOPE_HANDLE_ERRORS') == 'False':
            environ['wsgi.handleErrors'] = False
        def my_start_response(status, headers, exc_info=None):
            headers = sorted(headers)
            headers.insert(0, ('Status', status))
            return start_response(status, sorted(headers), exc_info=exc_info)
        return self.application(environ, my_start_response)


def wsgi_intercept_layer(layer):

    def make_debug_application():
        return ErrorHandler(layer.make_application())

    def setUp(cls):
        wsgi_intercept.add_wsgi_intercept('localhost', 80, make_debug_application)
    layer.setUp = classmethod(setUp)

    def tearDown(cls):
        wsgi_intercept.remove_wsgi_intercept('localhost', 80)

    def null(cls):
        pass
    layer.testSetUp = classmethod(null)
    layer.testTearDown = classmethod(null)
