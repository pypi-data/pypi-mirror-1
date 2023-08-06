"""entity classes for zone entities

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.mixins import TreeMixIn

class Zone(TreeMixIn, AnyEntity):
    """customized class for Zone entities"""
    __regid__ = 'Zone'
    fetch_attrs, fetch_order = fetch_config(['name'])
    tree_attribute = 'situated_in'
