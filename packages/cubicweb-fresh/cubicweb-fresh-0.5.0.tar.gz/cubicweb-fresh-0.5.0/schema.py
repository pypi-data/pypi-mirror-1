# template's specific schema
from yams.buildobjs import RelationDefinition
from cubicweb.schema import RRQLExpression

class spent_for(RelationDefinition):
    subject = 'Expense'
    object = 'Workcase'
    cardinality = '?*'
    __permissions__ = {
        'read' : ('managers', 'users'),
        'add': ('managers', RRQLExpression('S in_state ST, NOT ST name "accepted"')),
        'delete': ('managers', RRQLExpression('S in_state ST, NOT ST name "accepted"')),
        }
