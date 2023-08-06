from yams.buildobjs import (EntityType, SubjectRelation, ObjectRelation,
                            String, Datetime, Int)

from yams.constraints import IntervalBoundConstraint

_ = unicode

from cubicweb.schemas.base import CWUser
from cubes.folder.schema import Folder

from cubicweb.schema import ERQLExpression

class Masters(EntityType): # XXX find a suitable name
    """relation promoted to EntityType to store the `rate` attribute
    """
    __permissions__ = {'read': ('managers', 'users'),
                       'add': ('managers', ERQLExpression('X foruser U')),
                       'update': ('managers', 'owners'),
                       'delete': ('managers',),
                       }
    rate = Int(required=True, constraints=[IntervalBoundConstraint(0, 5)])
    foruser = SubjectRelation('CWUser', cardinality='1*')
    skill = SubjectRelation(('Technology', 'Folder'), cardinality='1*')


class Technology(Folder):
    pass

# extend CWUser
CWUser.add_relation(SubjectRelation(('Technology', 'Folder')), name='wishes_to_learn')
CWUser.add_relation(SubjectRelation('Talk', cardinality='**'), name='interested_in')

class Talk(EntityType):
    """relation promoted to EntityType to store the `subject' attribute
    """
    subject        = String(required=True, fulltextindexed=True, indexed=True, maxsize=32)
    description    = String(fulltextindexed=True,
                            description=_('more detailed subject description'))
    talktime       = Datetime(description=_('estimated presentation date'))
    presented_by   = SubjectRelation('CWUser', cardinality='?*')
    attended_by    = SubjectRelation('CWUser', cardinality='**')
    talks_about    = SubjectRelation(('Technology','Folder'), cardinality='+*')
    comments       = ObjectRelation('Comment', cardinality='1*', composite='object')
