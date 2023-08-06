"""cubicweb-nosylist

nosy list a la roundup

to use this cube:

1. add to your schema
   .. sourcecode:: python

     CWUser interested_in X
     X nosy_list CWUser

   where X are entity types considered as notification base, eg controlling
   who will be notified for events related to X.


2. configure on which relation the nosy list should be propagated
   .. sourcecode:: python

     from cubes.nosylist import hooks

     # relations where the "main" entity (eg holding the reference nosy list, so
     # should be in one `X` types cited above) is the subject of the relation
     securityhooks.S_RELS |= set(('documented_by', 'attachment', 'screenshot'))

     # relations where the "main" entity (eg holding the reference nosy list, so
     # should be in one `X` types cited above) is the object of the relation
     securityhooks.O_RELS |= set(('for_version', 'comments'))

3. write hooks that add user to nosy list when desired (for instance, when a
   user is adding a comment to an entity, add him to the entity's nosy list)

4. define your notification views / hooks, which should rely on the default
   recipients finder mecanism to get notified users (automatic if you're using
   cubicweb base classes)
"""
