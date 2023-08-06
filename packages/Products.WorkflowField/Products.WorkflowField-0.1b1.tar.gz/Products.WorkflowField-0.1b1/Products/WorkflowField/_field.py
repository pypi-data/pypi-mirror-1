#
# Copyright 2008, BlueDynamics Alliance, Austria - http://www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later 

__author__ = """Jens Klein <jens@bluedynamics.com>"""

from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes.interfaces.vocabulary import IVocabulary
from Products.Archetypes.atapi import Field
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.utils import OrderedDict
from Products.Archetypes.Registry import registerField
from Products.CMFCore.utils import getToolByName
from _widget import WorkflowWidget

class TransitionsVocabulary(object):
    
    __implements__ = (IVocabulary,)

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')
    
    def __init__(self, *args, **kwargs):
        pass
    
    def getDisplayList(self, instance):
        items = self._getItems(instance)
        return DisplayList(items)
    
    def getVocabularyDict(self, instance):
        items = self._getItems(instance)
        return OrderedDict(items)
    
    def _getItems(self, instance):
        wft = getToolByName(instance, 'portal_workflow')
        currentstate = wft.getInfoFor(instance, 'review_state')
        currentstate_title = wft.getTitleForStateOnType(
            currentstate, instance.getPortalTypeName())
        result = list()
        result.append( (currentstate, currentstate_title) )
        for wfaction in wft.listActionInfos(object=instance):
            result.append( (wfaction['id'], 
                            wfaction['title'] or wfaction['id']) )
        return result
    
    def isFlat(self):
        return True
    
    def showLeafsOnly(self):
        return True


class WorkflowField(Field):

    _properties = Field._properties.copy()
    _properties.update({
        'type' : 'dtml',
        'required': False,
        'workflow': None,
        'variable': 'review_state',
        'vocabulary': TransitionsVocabulary(),
        'widget': WorkflowWidget,
    })

    security  = ClassSecurityInfo()

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        wft = getToolByName(instance, 'portal_workflow')
        value = wft.getInfoFor(instance, 'review_state')
        return value

    security.declarePrivate('getRaw')
    def getRaw(self, instance, **kwargs):
        return self.get(instance, **kwargs)

    security.declarePrivate('set')
    def set(self, instance, value, comment=None, **kwargs):
        wft = getToolByName(instance, 'portal_workflow')
        if not value or value == wft.getInfoFor(instance, 'review_state'):
            return
        if self.workflow is None:
            wft.doActionFor(instance, action=value, comment=comment)
        else:
            wft.doActionFor(instance, action=value, wf_id=self.workflow, 
                comment=comment)

registerField(
    WorkflowField,
    title="Workflow Field",
    description=("A field to do workflow transitions")
)
