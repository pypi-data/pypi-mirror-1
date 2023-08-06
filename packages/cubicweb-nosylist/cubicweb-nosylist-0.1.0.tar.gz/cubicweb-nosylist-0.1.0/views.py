"""nosy list views

:organization: Logilab
:copyright: 2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.selectors import relation_possible
from cubicweb.view import Component
from cubicweb.web import uicfg

_pvs = uicfg.primaryview_section
_pvs.tag_object_of(('*', 'interested_in', '*'), 'hidden')
_pvs.tag_object_of(('*', 'nosy_list', '*'), 'hidden')
_pvs.tag_subject_of(('*', 'nosy_list', '*'), 'hidden')

_afs = uicfg.autoform_section
_afs.tag_subject_of(('*', 'nosy_list', '*'), 'generated')
_afs.tag_object_of(('*', 'nosy_list', '*'), 'generated')
_afs.tag_subject_of(('*', 'interested_in', '*'), 'generic')
_afs.tag_object_of(('*', 'interested_in', '*'), 'metadata')


class NotificationComponent(Component):
    """component to control explicit registration for notification on an entity
    (eg interested_in relation)"""
    id = 'notification'
    __select__ = (Component.__select__ &
                  relation_possible('interested_in', 'object', 'CWUser',
                                    action='add'))

    context = 'header'

    def call(self):
        req = self.req
        user = req.user
        entity = self.rset.get_entity(self.row or 0, self.col or 0)
        self.w(u'<div class="%s" id="%s">' % (self.id, self.div_id()))
        title = req._('click here if you don\'t want to be notified anymore for this %s'
                      % entity.dc_type())
        imgurl = req.external_resource('MAIL_ICON')
        msg = req._('you are not anymore registered for this %s'
                    % entity.dc_type())
        if self.has_user_interest(user, entity):
            # user is explicitly registered
            rql = 'DELETE U interested_in X WHERE U eid %(u)s, X eid %(x)s'
        elif self.user_in_nosy_list(user, entity):
            # user is implicitly registered
            rql = 'DELETE U interested_in X WHERE U eid %(u)s, X eid %(x)s'
        else:
            # user isn't registered
            rql = 'SET U interested_in X WHERE U eid %(u)s, X eid %(x)s'
            title = req._('click here to be notified about changes for this %s'
                               % entity.dc_type())
            imgurl = req.external_resource('NOMAIL_ICON')
            msg = _('you are now registered for this %s' % entity.dc_type())
        url = self.user_rql_callback((rql, {'u': user.eid, 'x': entity.eid}, 'x'),
                                     msg=msg)
        self.w(u'<a href="%s" title="%s"><img src="%s" alt="%s"/></a>' % (
            url, title, imgurl, title))
        self.w(u'</div>')
        self.w(u'<div class="clear"></div>')

    def has_user_interest(self, user, entity):
        """return true if the user is currently interested in the entity"""
        return bool(self.req.execute('Any X WHERE U interested_in X, U eid %(u)s, X eid %(x)s',
                                     {'u': user.eid, 'x': entity.eid}, 'x'))

    def user_in_nosy_list(self, user, entity):
        """return true if the user is in the nosy list for the entity"""
        return bool(self.req.execute('Any X WHERE X nosy_list U, U eid %(u)s, X eid %(x)s',
                                     {'u': user.eid, 'x': entity.eid}, 'x'))
