"""this contains the template-specific entities' classes

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.mixins import TreeMixIn
from cubicweb.interfaces import ITree

class Division(AnyEntity):
    """customized class for Division entities"""
    __regid__ = 'Division'
    fetch_attrs, fetch_order = fetch_config(['name'])

class Company(TreeMixIn, Division):
    """customized class for Company entities"""
    __regid__ = 'Company'
    __implements__ = AnyEntity.__implements__ + (ITree,)
    tree_attribute = 'subsidiary_of'
