"""nosy list views

:organization: Logilab
:copyright: 2009-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.selectors import relation_possible
from cubicweb.web import uicfg, component
from logilab.mtconverter import xml_escape

_pvs = uicfg.primaryview_section
_pvs.tag_object_of(('*', 'interested_in', '*'), 'hidden')
_pvs.tag_object_of(('*', 'nosy_list', '*'), 'hidden')
_pvs.tag_subject_of(('*', 'nosy_list', '*'), 'hidden')

_afs = uicfg.autoform_section
_afs.tag_subject_of(('*', 'nosy_list', '*'), 'main', 'hidden')
_afs.tag_object_of(('*', 'nosy_list', '*'), 'main', 'hidden')
_afs.tag_subject_of(('*', 'interested_in', '*'), 'main', 'relations')
_afs.tag_object_of(('*', 'interested_in', '*'), 'main', 'metadata')


class NotificationComponent(component.EntityVComponent):
    """component to control explicit registration for notification on an entity
    (eg interested_in relation)"""
    __regid__ = 'notification'
    __select__ = (component.EntityVComponent.__select__ &
                  relation_possible('interested_in', 'object', 'CWUser',
                                    action='add'))
    context = 'ctxtoolbar'

    def call(self, view=None):
        self.cell_call(self.row or 0, self.col or 0)

    def cell_call(self, row, col, view=None):
        req = self._cw
        user = req.user
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<div class="toolbarButton" id="notificationComponent-%s">'
               % entity.eid)
        title = req._('Click here if you don\'t want to be notified anymore for this %s'
                      ) % entity.dc_type()
        imgurl = req.external_resource('MAIL_ICON')
        msg = req._('you are not anymore registered for this %s'
                    ) % entity.dc_type()
        if self.has_user_interest(user, entity):
            # user is explicitly registered
            rql = 'DELETE U interested_in X WHERE U eid %(u)s, X eid %(x)s'
        elif self.user_in_nosy_list(user, entity):
            # user is implicitly registered
            rql = 'DELETE X nosy_list U WHERE U eid %(u)s, X eid %(x)s'
        else:
            # user isn't registered
            rql = 'SET U interested_in X WHERE U eid %(u)s, X eid %(x)s'
            title = req._('Click here to be notified about changes for this %s'
                          ) % entity.dc_type()
            imgurl = req.external_resource('NOMAIL_ICON')
            msg = req._('you are now registered for this %s'
                    ) % entity.dc_type()
        url = self._cw.user_rql_callback((rql, {'u': user.eid, 'x': entity.eid}, 'x'),
                                         msg=msg)
        self.w(u'<a href="%s" title="%s"><img src="%s" alt="%s"/></a>' % (
            xml_escape(url), xml_escape(title), xml_escape(imgurl),
            xml_escape(title)))
        self.w(u'</div>')

    def has_user_interest(self, user, entity):
        """return true if the user is currently interested in the entity"""
        return bool(self._cw.execute(
            'Any X WHERE U interested_in X, U eid %(u)s, X eid %(x)s',
            {'u': user.eid, 'x': entity.eid}, 'x'))

    def user_in_nosy_list(self, user, entity):
        """return true if the user is in the nosy list for the entity"""
        return bool(self._cw.execute(
            'Any X WHERE X nosy_list U, U eid %(u)s, X eid %(x)s',
            {'u': user.eid, 'x': entity.eid}, 'x'))
