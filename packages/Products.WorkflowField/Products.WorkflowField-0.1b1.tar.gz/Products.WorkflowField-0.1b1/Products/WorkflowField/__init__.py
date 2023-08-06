#
# Copyright 2008, BlueDynamics Alliance, Austria - http://www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later 

__author__ = """Jens Klein <jens@bluedynamics.com>"""

from Products.WorkflowField._field import WorkflowField
from Products.WorkflowField._widget import WorkflowWidget

from Products.CMFCore import permissions
from Products.Archetypes import public as atapi
from Products.CMFCore import utils as cmfutils

# Product initialization
def initialize(context):
    import examples.content

    project_name = 'WorkflowField'

    # Process the project's types
    content_types, constructors, ftis = \
        atapi.process_types(atapi.listTypes(project_name), project_name)

    cmfutils.ContentInit(
        meta_type           = project_name + ' Content',
        content_types       = content_types,
        permission          = permissions.AddPortalContent,
        extra_constructors  = constructors,
        fti                 = ftis,
    ).initialize(context)
