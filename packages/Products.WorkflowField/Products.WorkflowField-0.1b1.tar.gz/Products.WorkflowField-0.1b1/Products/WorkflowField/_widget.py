#
# Copyright 2008, BlueDynamics Alliance, Austria - http://www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later 

__author__ = """Jens Klein <jens@bluedynamics.com>"""

from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.atapi import SelectionWidget

class WorkflowWidget(SelectionWidget):
    
    _properties = SelectionWidget._properties.copy()
    _properties.update({
            'macro': 'workflow_widget',
            'visible': {'view': 'invisible',
                        'edit': 'visible'},
            'format': 'radio',
            'allow_comments': False,
            'label_comments': 'Comments',
            'label_comments_msgid': 'label_comments',
            'help_comments': 'Will be added to the publishing history.',
            'help_comments_msgid': 'help_comments',
            'i18n_domain': 'WorkflowField'
    })

    def process_form(self, instance, field, form, empty_marker=None,
        emptyReturnsMarker=False):
        """ Processes input passing the transtion and comments to the 
            field object.
        """
        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            return empty_marker
        if emptyReturnsMarker and value == '':
            return empty_marker

        comment = form.get(field.getName() + '_wfcomment', None)
        kwargs = {'comment': comment}

        return value, kwargs

    def labelComments(self, instance):
        return self._translate_attribute(instance, 'label_comments')

    def helpComments(self, instance):
        return self._translate_attribute(instance, 'help_comments')


registerWidget(WorkflowWidget,
               title='Workflow',
               description=('Can be used to do workflow actions.'),
               used_for=('Products.WorkflowField.WorkflowField',)
               )    
