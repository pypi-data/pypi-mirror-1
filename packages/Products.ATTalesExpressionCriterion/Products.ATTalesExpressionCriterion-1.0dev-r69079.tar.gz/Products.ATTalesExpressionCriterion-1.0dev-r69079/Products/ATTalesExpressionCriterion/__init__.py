#
import logging

from Products.Archetypes.atapi import process_types, listTypes
from Products.ATContentTypes.permission import ChangeTopics

from Products.CMFCore.utils import ContentInit
from Products.CMFPlone.utils  import ToolInit

from Products.ATTalesExpressionCriterion.config import PROJECTNAME
from zope.i18nmessageid import MessageFactory

ATTalesExpressionCriterionMessageFactory = MessageFactory(PROJECTNAME)
logger = logging.getLogger(PROJECTNAME)

# Add object implements
import Products.ATTalesExpressionCriterion.criteria

# wire the add permission after all types are registered
from Products.ATContentTypes.permission import wireAddPermissions
wireAddPermissions()

def initialize(context):
    ##Import Types here to register them

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    ContentInit(
       PROJECTNAME + ' Content',
       content_types      = content_types,
       permission         = ChangeTopics,
       extra_constructors = constructors,
       fti                = ftis,
       ).initialize(context)

