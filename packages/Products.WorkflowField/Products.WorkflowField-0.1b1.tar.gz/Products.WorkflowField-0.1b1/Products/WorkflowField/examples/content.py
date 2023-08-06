""" Example content type using WorkflowField.
"""

from Products.Archetypes import public as atapi
from Products.WorkflowField import WorkflowField, WorkflowWidget

schema = atapi.BaseSchema.copy() + atapi.Schema((
    WorkflowField(
        'status',
        workflow = 'simple_publication_workflow',
        accessor = 'getReviewState',
        mutator = 'setReviewState',
        widget = WorkflowWidget(
            label = 'Review State',
            description = 'Select the action to the next state.',
            allow_comments = True,
        ),
    ),
))

class ExampleWFFieldContent(atapi.BaseContent):
    """
    ExampleWFFieldContent.
    """

    portal_type = meta_type = 'ExampleWFFieldContent'
    archetype_name = 'ExampleWFField Content'

    schema = schema

atapi.registerType(ExampleWFFieldContent)
