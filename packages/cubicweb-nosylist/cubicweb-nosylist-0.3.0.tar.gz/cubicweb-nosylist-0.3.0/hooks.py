from itertools import chain

from logilab.common.decorators import classproperty

from cubicweb.server.hook import (Hook, PropagateSubjectRelationHook,
                                  PropagateSubjectRelationAddHook,
                                  PropagateSubjectRelationDelHook,
                                  match_rtype, match_rtype_sets)
from cubicweb.selectors import implements

from cubes.nosylist.interfaces import INosyList

class INotificationBaseAddedHook(Hook):
    """automatically register the user creating a ticket as interested by it
    """
    __regid__ = 'notification_base_added_hook'
    __select__ = Hook.__select__ & implements(INosyList)
    events = ('after_add_entity',)

    def __call__(self):
        session = self._cw
        entity = self.entity
        if not session.is_internal_session:
            asession = session.actual_session()
            asession.execute('SET U interested_in X WHERE X eid %(x)s, U eid %(u)s',
                             {'x': entity.eid, 'u': asession.user.eid}, 'x')


class InterestedInAddHook(Hook):
    """adds relation nosy_list corresponding to relation interested_in
    """
    __regid__ = 'add_interested_in_hook'
    __select__ = Hook.__select__ & match_rtype('interested_in')
    events = ('after_add_relation',)

    def __call__(self):
        session = self._cw
        fromeid = self.eidfrom
        toeid = self.eidto
        session.unsafe_execute('SET X nosy_list U WHERE X eid %(x)s, U eid %(u)s, '
                               'NOT X nosy_list U',
                               {'x': toeid, 'u': fromeid}, 'x')


class InterestedInDelHook(Hook):
    """deletes relation nosy_list corresponding to relation interested_in
    """
    __regid__ = 'deleted_interested_in_hook'
    __select__ = Hook.__select__ & match_rtype('interested_in')
    events = ('after_delete_relation',)

    def __call__(self):
        session = self._cw
        fromeid = self.eidfrom
        toeid = self.eidto
        session.unsafe_execute('DELETE X nosy_list U WHERE X eid %(x)s, U eid %(u)s',
                               {'x': toeid, 'u': fromeid}, 'x')


# relations where the "main" entity is the subject
S_RELS = set()
# relations where the "main" entity is the object
O_RELS = set()

class NosyListPropagationHook(PropagateSubjectRelationHook):
    """propagate permissions when new entity are added"""
    __regid__ = 'nosy_list_propagation_hook'
    __select__ = Hook.__select__ & match_rtype_sets(S_RELS, O_RELS)

    main_rtype = 'nosy_list'
    subject_relations = S_RELS
    object_relations = O_RELS


class NosyListAddPropagationHook(PropagateSubjectRelationAddHook):
    """propagate permissions when new entity are added"""
    __regid__ = 'nosy_list_add_propagation_hook'
    __select__ = Hook.__select__ & match_rtype('nosy_list')

    subject_relations = S_RELS
    object_relations = O_RELS


class NosyListDelPropagationHook(PropagateSubjectRelationDelHook):
    __regid__ = 'nosy_list_del_propagation_hook'
    __select__ = Hook.__select__ & match_rtype('nosy_list')

    subject_relations = S_RELS
    object_relations = O_RELS
