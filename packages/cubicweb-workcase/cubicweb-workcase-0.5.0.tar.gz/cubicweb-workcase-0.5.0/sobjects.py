"""this contains the server-side objects"""

from cubicweb import ValidationError

from cubicweb.server.hooksmanager import Hook

def check_wptitle(session, workcase, workpackage):
    """checks that `workpackage`'s title doesn't conflict with
    an existing workpackage in the same workcase
    """
    title = workpackage.title
    existing_wps = [wp.title for wp in workcase.split_into]
    if title in existing_wps:
        msg = 'There is already a workpackage named %s in this workcase'
        raise ValidationError(workpackage.eid,
                              {'title': session._(msg) % title})


class BeforeAddSplitIntoRelation(Hook):
    """checks that the new workpackage's title doesn't conflict with
    an existing workpackage in the same workcase
    """
    events = ('before_add_relation',)
    accepts = ('split_into',)

    def call(self, session, fromeid, rtype, toeid):
        check_wptitle(session, session.entity_from_eid(fromeid),
                      session.entity_from_eid(toeid))


class CheckWPName(Hook):
    """checks that the new workpackage's title doesn't conflict with
    an existing workpackage in the same workcase
    """
    events = ('before_update_entity',)
    accepts = ('Workpackage',)

    def call(self, session, entity):
        if 'title' in entity:
            # if the user hasn't updated/edited the title
            # it does not exist in the entity's dict-like interface
            check_wptitle(session, entity.reverse_split_into[0], entity)

