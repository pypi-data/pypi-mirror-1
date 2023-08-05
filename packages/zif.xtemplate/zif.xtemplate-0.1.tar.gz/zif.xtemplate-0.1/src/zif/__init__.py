"""
$Id: __init__.py 9 2006-12-16 04:22:32Z fairwinds $

zif.xtemplate
Copyright (c) 2006, Virginia Polytechnic Institute and State University
All rights reserved. Refer to LICENSE.txt for details of distribution and use.

Namespace package
 
"""

try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError, e:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
