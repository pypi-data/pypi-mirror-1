##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2003-2006 AT Content Types development team
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Topic:


"""

__author__  = 'Andreas Gabriel <gabriel@hrz.uni-marburg.de>'
__docformat__ = 'restructuredtext'

from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import Schema, registerType

from Products.TALESField import TALESString
from Products.Archetypes.atapi import StringWidget

from Products.ATContentTypes.criteria import _criterionRegistry, registerCriterion, \
    STRING_INDICES

from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.permission import ChangeTopics
from Products.ATContentTypes.criteria.base import ATBaseCriterion
from Products.ATContentTypes.criteria.schemata import ATBaseCriterionSchema

from Products.ATTalesExpressionCriterion import ATTalesExpressionCriterionMessageFactory as _

from Products.ATTalesExpressionCriterion.config import PROJECTNAME

ATTalesExpressionCriterionSchema = ATBaseCriterionSchema + Schema((
    TALESString('value',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Value",
                mutator="setValue",
                widget=StringWidget(
                    label=_(u'label_tales_criteria_value', default=u'Value'),
                    description=_(u'help_tales_criteria_value',
                                  default=u'A tales expression.'))
                ),
    ))

class ATTalesExpressionCriterion(ATBaseCriterion):
    """A tales expression criterion"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion, )
    security       = ClassSecurityInfo()
    schema         = ATTalesExpressionCriterionSchema
    meta_type      = 'ATTalesExpressionCriterion'
    archetype_name = 'Tales Expression Criterion'
    shortDesc      = 'Expression'

    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []

        if self.Value() is not '':
            result.append((self.Field(), self.Value()))

        return tuple( result )

registerCriterion(ATTalesExpressionCriterion, STRING_INDICES)


