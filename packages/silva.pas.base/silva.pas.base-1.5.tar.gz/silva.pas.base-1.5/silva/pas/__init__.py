# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: __init__.py 28109 2008-03-19 11:33:54Z sylvain $

# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
