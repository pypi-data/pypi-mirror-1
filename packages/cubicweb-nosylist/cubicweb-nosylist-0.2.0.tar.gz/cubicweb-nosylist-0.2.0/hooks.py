from itertools import chain

from logilab.common.decorators import classproperty

from cubicweb.server import hooksmanager

class INotificationBaseAddedHook(hooksmanager.Hook):
    """automatically register the user creating a ticket as interested by it
    """
    events = ('after_add_entity',)
    accepts = [] # XXX INotificationBase w/ cw 3.5

    def call(self, session, entity):
        if not session.is_internal_session:
            asession = session.actual_session()
            asession.execute('SET U interested_in X WHERE X eid %(x)s, U eid %(u)s',
                             {'x': entity.eid, 'u': asession.user.eid}, 'x')


class InterestedInAddHook(hooksmanager.Hook):
    """adds relation nosy_list corresponding to relation interested_in
    """
    events = ('after_add_relation',)
    accepts = ('interested_in',)

    def call(self, session, fromeid, rtype, toeid):
        session.unsafe_execute('SET X nosy_list U WHERE X eid %(x)s, U eid %(u)s, '
                               'NOT X nosy_list U',
                               {'x': toeid, 'u': fromeid}, 'x')


class InterestedInDelHook(hooksmanager.Hook):
    """deletes relation nosy_list corresponding to relation interested_in
    """
    events = ('after_delete_relation',)
    accepts = ('interested_in',)

    def call(self, session, fromeid, rtype, toeid):
        session.unsafe_execute('DELETE X nosy_list U WHERE X eid %(x)s, U eid %(u)s',
                               {'x': toeid, 'u': fromeid}, 'x')


# relations where the "main" entity is the subject
S_RELS = set()
# relations where the "main" entity is the object
O_RELS = set()


class NosyListPropagationHook(hooksmanager.PropagateSubjectRelationHook):
    """propagate permissions when new entity are added"""
    rtype = 'nosy_list'
    subject_relations = S_RELS
    object_relations = O_RELS

    @classproperty
    def accepts(cls):
        return chain(cls.subject_relations, cls.object_relations)

class NosyListAddPropagationHook(hooksmanager.PropagateSubjectRelationAddHook):
    """propagate permissions when new entity are added"""
    rtype = 'nosy_list'
    subject_relations = S_RELS
    object_relations = O_RELS
    accepts = ('nosy_list',)

class NosyListDelPropagationHook(hooksmanager.PropagateSubjectRelationDelHook):
    rtype = 'nosy_list'
    subject_relations = S_RELS
    object_relations = O_RELS
    accepts = ('nosy_list',)
