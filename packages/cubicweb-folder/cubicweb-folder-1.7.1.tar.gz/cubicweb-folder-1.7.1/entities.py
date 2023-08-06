"""entity classes for Folder entities

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
from itertools import chain

from cubicweb.mixins import TreeMixIn
from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.interfaces import ITree


class Folder(TreeMixIn, AnyEntity):
    """customized class for Folder entities"""
    __regid__ = 'Folder'
    __implements__ = AnyEntity.__implements__ + (ITree,)
    fetch_attrs, fetch_order = fetch_config(['name'])

    tree_attribute = 'filed_under'
