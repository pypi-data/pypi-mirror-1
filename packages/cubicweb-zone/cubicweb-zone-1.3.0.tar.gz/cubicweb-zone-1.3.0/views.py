from cubicweb.view import EntityView
from cubicweb.mixins import TreePathMixIn
from cubicweb.selectors import implements
from cubicweb.web import uicfg, facet

_abaa = uicfg.actionbox_appearsin_addmenu
_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl

_abaa.tag_object_of(('Zone', 'situated_in', 'Zone'), True)
_pvs.tag_subject_of(('Zone', 'situated_in', 'Zone'), 'hidden')
_pvdc.tag_attribute(('Zone', 'description'), {'showlabel': False})


class SituatedInFacet(facet.RelationFacet):
    __regid__ = 'situated_in-facet'
    rtype = 'situated_in'
    target_attr = 'name'
    label_vid = 'combobox'

# XXX code below almost copied/paste from folder. Should be written for ITree.
#     more like this in the folder cube

class ZonePathBarView(TreePathMixIn, EntityView):
    """one zone in the zone path bar"""
    __select__ = implements('Zone')
    separator = u'&nbsp;&gt;&nbsp;'


class ZoneComboBoxView(ZonePathBarView):
    """display zone in edition's combobox"""
    __select__ = implements('Zone')
    __regid__ = 'combobox'
    item_vid = 'text'
    separator = u' > '
