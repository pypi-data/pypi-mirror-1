"""nosy list based recipients finder

:organization: Logilab
:copyright: 2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.selectors import relation_possible
from cubicweb.sobjects.notification import RecipientsFinder

class NosyListRecipientsFinder(RecipientsFinder):
    __select__ = relation_possible('nosy_list', 'subject')

    def recipients(self):
        """Returns users in the nosy list for the entity"""
        entity = self.cw_rset.get_entity(0, 0)
        rql = ('Any U, E, A WHERE X nosy_list U, X eid %(e)s, U in_state S, '
               'S name "activated", U primary_email E, E address A')
        # use unsafe_execute since user don't necessarily have access to
        # all users which should be notified
        rset = self._cw.unsafe_execute(rql, {'e': entity.eid}, 'e',
                                       build_descr=True, propagate=True)
        return list(rset.entities()) # we don't want an iterator but a list
