from yams.buildobjs import (EntityType, RelationType, RelationDefinition,
                            SubjectRelation, ObjectRelation,
                            String, Date, Datetime)
from cubicweb.schema import WorkflowableEntityType

try:
    from cubes.person.schema import Person
    from cubes.task.schema import Task
    from cubes.event.schema import Event
except (ImportError, NameError):
    # old-style yams schema will raise NameError on EntityType, RelationType, etc.
    Person = import_erschema('Person')
    Task = import_erschema('Task')
    Event = import_erschema('Event')

Person.add_relation(Date(), name='birthday')
Person.add_relation(ObjectRelation('Comment', cardinality='1*', composite='object'), name='comments')
Person.add_relation(ObjectRelation('Tag'), name='tags')
Person.add_relation(SubjectRelation('File'), name='concerned_by')


Task.add_relation(ObjectRelation('Comment', cardinality='1*', composite='object'), name='comments')
Task.add_relation(SubjectRelation('Person'), name='todo_by')

Event.add_relation(ObjectRelation('Comment', cardinality='1*', composite='object'), name='comments')


class School(EntityType):
    """an (high) school"""
    name   = String(required=True, fulltextindexed=True, maxsize=128)
    address   = String(maxsize=512)
    description = String(fulltextindexed=True)

    phone         = SubjectRelation('PhoneNumber', composite='subject')
    use_email     = SubjectRelation('EmailAddress', composite='subject')

    has_studied_in = ObjectRelation('Person')


class has_studied_in(RelationType):
    """used to indicate an estabishment where a person has been studying"""
    # XXX promotion?


class interested_in(RelationDefinition):
    subject = ('Person', 'CWUser')
    object = 'Event'


class Application(WorkflowableEntityType):
    for_person = SubjectRelation('Person', cardinality='1*', composite='object')
    date = Datetime(default='TODAY', required=True)
    tags = ObjectRelation('Tag')
    topic = ObjectRelation('EmailThread')


