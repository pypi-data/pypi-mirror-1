"""specific task views

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from datetime import date

from cubicweb.selectors import implements
from cubicweb.web import uicfg
from cubicweb.web.views import primary
from cubicweb.web import uicfg

uicfg.primaryview_section.tag_subject_of(('Task', 'todo_by', '*'), 'attributes')
uicfg.primaryview_section.tag_subject_of(('Task', 'todo_by', '*'), 'sideboxes')
uicfg.primaryview_section.tag_attribute(('Task', 'start'), 'hidden')
uicfg.primaryview_section.tag_attribute(('Task', 'stop'), 'hidden')

uicfg.actionbox_appearsin_addmenu.tag_object_of(('Task', 'todo_by', 'CWUser'), True)
uicfg.actionbox_appearsin_addmenu.tag_subject_of(('Task', 'depends_on', 'Task'), True)
uicfg.actionbox_appearsin_addmenu.tag_object_of(('Task', 'depends_on', 'Task'), True)

uicfg.autoform_field_kwargs.tag_attribute(
    ('Task', 'start'),
    {'value': lambda form: form._cw.format_date(date.today())})

class TaskPrimaryView(primary.PrimaryView):
    __select__ = implements('Task')

    def render_entity_attributes(self, entity):
        self.w(u'<h2>%s - %s</h2>' % (self._cw.format_date(entity.start),
                                      self._cw.format_date(entity.stop)))
        super(TaskPrimaryView, self).render_entity_attributes(entity)


