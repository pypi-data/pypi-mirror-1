# -*- coding: utf-8 -*-
#
# Copyright (c) 2003-2007 by H. Turgut Uyar <uyar@itu.edu.tr>
#
# This file is part of CMFQuestionnaire.
#
# CMFQuestionnaire is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# CMFQuestionnaire is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = """H. Turgut Uyar <uyar@itu.edu.tr>"""
__docformat__ = "restructuredtext"


from AccessControl import ModuleSecurityInfo
from Products.CMFCore import utils
from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFQuestionnaire.config import PROJECTNAME
from zope.i18nmessageid import MessageFactory

QuestionnaireMessageFactory = MessageFactory("cmfquestionnaire")
ModuleSecurityInfo("Products.CMFQuestionnaire").declarePublic("QuestionnaireMessageFactory")


def initialize(context):
    from Questionnaire import Questionnaire
    content_types, constructors, ftis = process_types(listTypes(PROJECTNAME),
                                                      PROJECTNAME)

    import permissions as perms
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        utils.ContentInit(kind,
                          content_types=(atype,),
                          permission=getattr(perms, "Add%s" % atype.meta_type),
                          extra_constructors=(constructor,),
                          fti=ftis).initialize(context)
