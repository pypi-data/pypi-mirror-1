from yams.buildobjs import (EntityType, RelationType, SubjectRelation,
                            ObjectRelation, String, Datetime, Int, RichString)
from cubicweb.schema import RichString

from cubicweb.schema import RQLConstraint, WorkflowableEntityType

class Task(WorkflowableEntityType):
    """something to do"""
    title  = String(required=True, fulltextindexed=True, maxsize=64)
    start  = Datetime(default='TODAY')
    stop   = Datetime(default='TODAY')
    author = String(fulltextindexed=True,  maxsize=12)
    cost   = Int()

    description = RichString(fulltextindexed=True)

    todo_by = SubjectRelation('CWUser')
    depends_on = SubjectRelation('Task')


class todo_by(RelationType):
    """"""

class depends_on(RelationType):
    """"""

