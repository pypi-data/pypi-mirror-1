# cube's specific schema
"""

:organization: Logilab
:copyright: 2001-2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""
from yams.reader import context
from yams.buildobjs import RelationType, SubjectRelation, ObjectRelation, String
from cubicweb.schema import WorkflowableEntityType
from cubes.tracker.schemaperms import oexpr, sexpr

try:
    from cubes.card.schema import Card
    from cubes.tracker.schema import Ticket, Version
    from cubes.comment.schema import Comment
except (ImportError, NameError):
    Card = import_erschema('Card')
    Ticket = import_erschema('Ticket')
    Version = import_erschema('Version')
    Comment = import_erschema('Comment')


class TestInstance(WorkflowableEntityType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (), # handled by hook
        'update': ('managers',),
        'delete': ('managers',),
        }
    ## attributes
    # name size constraint should be the same as Card's title
    name  = String(required=True, fulltextindexed=True, maxsize=256)
    ## relations
    instance_of = SubjectRelation('Card', cardinality='1*', composite='object')
    for_version = SubjectRelation('Version', cardinality='1*', composite='object')
    generate_bug = SubjectRelation('Ticket', description=_('link to a bug encountered while passing the test'))

    if 'Comment' in context.defined:
        comments = ObjectRelation('Comment', cardinality='1*', composite='object')

class test_case_of(RelationType):
    """specify that a card is describing a test for a project"""
    subject = 'Card'
    object = 'Project'
    cardinality = '?*'
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', oexpr('developer', 'client'),),
        'delete': ('managers', 'staff', oexpr('developer', 'client'),),
        }

class test_case_for(RelationType):
    """specify that a card is describing a test for a particular story"""
    subject = 'Card'
    object = 'Ticket'
    cardinality = '?*'
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', oexpr('developer', 'client'),),
        'delete': ('managers', 'staff', oexpr('developer', 'client'),),
        }
class for_version(RelationType):
    inlined = True
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (), # handled by hook
        'delete': ('managers', 'users',), # will need delete perm on TestInstance
        }
class generate_bug(RelationType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', sexpr('developer', 'client'),),
        'delete': ('managers', 'staff', sexpr('developer', 'client'),),
    }

class instance_of(RelationType):
    inlined = True
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (), # handled by hook
        'delete': ('managers', 'users',),
        }

