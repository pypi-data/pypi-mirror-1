# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: __init__.py 5447 2007-11-27 15:25:45Z sweh $

#namespace package boilerplate
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError, e:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)

