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


from Products.CMFCore import permissions
from Products.CMFCore.permissions import setDefaultRoles

ViewQuestionnaire = permissions.View

AddQuestionnaire = "CMFQuestionnaire: Add Questionnaire"
setDefaultRoles(AddQuestionnaire, ("Manager", "Owner"))

FilloutQuestionnaire = "CMFQuestionnaire: Fill-Out Questionnaire"
setDefaultRoles(FilloutQuestionnaire, ("Anonymous", "Authenticated"))

ViewQuestionnaireResults = "CMFQuestionnaire: View Results"
setDefaultRoles(ViewQuestionnaireResults, ("Manager", "Owner"))
