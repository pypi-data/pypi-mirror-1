"""template-specific forms/views/actions/components"""

from logilab.mtconverter import html_escape

from cubicweb.selectors import implements
from cubicweb.view import EntityView
from cubicweb.web import uicfg

uicfg.actionbox_appearsin_addmenu.tag_subject_of(('Workcase', 'split_into', 'Workpackage'), True)
uicfg.actionbox_appearsin_addmenu.tag_object_of(('Workcase', 'split_into', 'Workpackage'), False)

