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


import Globals
from persistent.list import PersistentList
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import TextField, TextAreaWidget
from Products.Archetypes.atapi import BooleanField, BooleanWidget
from Products.Archetypes.atapi import StringField, StringWidget
from Products.Archetypes.atapi import FloatField, DecimalWidget
from Products.Archetypes.atapi import LinesField, LinesWidget
from Products.Archetypes.atapi import FileField, FileWidget
from Products.Archetypes.atapi import DateTimeField, CalendarWidget
from Products.Archetypes.atapi import SelectionWidget
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFQuestionnaire import QuestionnaireMessageFactory as _
from Products.CMFQuestionnaire.config import PROJECTNAME
from Products.CMFQuestionnaire.config import PDF_REGULAR_FONT, PDF_ITALIC_FONT
from Products.CMFQuestionnaire.permissions import ViewQuestionnaire
from Products.CMFQuestionnaire.permissions import ViewQuestionnaireResults
from Products.CMFQuestionnaire.permissions import FilloutQuestionnaire

import os
import random
from xml.dom import minidom
from StringIO import StringIO
from DateTime import DateTime

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont("Serif", PDF_REGULAR_FONT))
    pdfmetrics.registerFont(TTFont("Serif-Italic", PDF_ITALIC_FONT))

    pdfAvailable = True
except:
    pdfAvailable = False

try:
    xlsAvailable = False
except:
    xlsAvailable = False


QuestionnaireSchema = ATContentTypeSchema.copy() + Schema((
    TextField(
        name="body",
        searchable=True,
        allowable_content_types=("txt/xml",),
        default="<questionnaire/>",
        widget=TextAreaWidget(
            label=_(u"label_xml_body",
                    default=u"XML Body"),
            description=_(u"help_xml_body",
                          default=u"Enter the XML body of the questionnaire. You may prefer to use the design tab instead of filling out this field manually."),
            modes=("edit",),
            ),
        ),

    TextField(
        name="answers",
        allowable_content_types=("txt/xml",),
        default="<answers/>",
        widget=TextAreaWidget(
            label=_(u"label_answers",
                    default=u"Answers"),
            modes=(),
            ),
        ),

    BooleanField(
        name="use_ticket",
        default=False,
        widget=BooleanWidget(
            label=_(u"label_use_ticket",
                    default=u"Use Ticket"),
            description=_(u"help_use_ticket",
                          default=u"Do you want to use tickets in addition to roles?"),
            ),
        ),
    ),)


finalizeATCTSchema(QuestionnaireSchema)


class Questionnaire(ATCTContent):
    """A questionnaire."""

    __implements__ = (ATCTContent.__implements__,)

    schema = QuestionnaireSchema

    security = ClassSecurityInfo()

    tags = {"q": "question", "g": "group"}

    leftX, topY = 50, 770
    limitX, limitY = 550, 30
    chartX, chartY = 270, 140

    security.declarePrivate("getChildrenByTagName")
    def getChildrenByTagName(self, parent, tagName):
        """
        Return the list of immediate children (with a given tag name) of the
        parent node.
        """

        return filter(lambda n: n.tagName==tagName, parent.childNodes)

    security.declarePrivate("createChild")
    def createChild(self, parent, name, attributes=None, text=None):
        """
        Return a newly created element with the given tag name. Create the
        element in the owner document of the parent node, set the given
        attributes, append a text node child if text is given, and append the
        newly created element to the children of the parent node.
        """

        o = parent.ownerDocument
        e = o.createElement(name)
        if attributes is not None:
            for a in attributes.keys():
                e.setAttribute(a, str(attributes[a]))
        if text is not None:
            t = o.createTextNode(text)
            e.appendChild(t)
        parent.appendChild(e)
        return e

    security.declarePrivate("getNextId")
    def getNextId(self, tagName, document=None):
        """
        Return the next id value for the given tag name. Ids are assumed to
        consist of a mnemonic and an integer value. The next id value is the
        one following the current maximum id for that tag name.
        """

        if document is None:
            dom = minidom.parseString(str(self.body))
            document = dom.documentElement
        max = 0
        for e in document.getElementsByTagName(tagName):
            id = int(e.getAttribute("id")[1:])
            if id > max:
                max = id
        return str(max+1)

    security.declarePrivate("getItemById")
    def getItemById(self, parent, itemId, tagName=None):
        """Return the item with the given id."""

        if tagName is None:
            tagName = self.tags[itemId[0]]
        items = parent.getElementsByTagName(tagName)
        for i in items:
            if i.getAttribute("id") == itemId:
                return i
        return None

    security.declareProtected(ViewQuestionnaire, "getItems")
    def getItems(self):
        """Return information of all top-level items."""

        dom = minidom.parseString(str(self.body))
        document = dom.documentElement
        result = []
        for n in document.childNodes:
            if n.tagName == "question":
                result.append(self.getQuestionInfo(n))
            elif n.tagName == "group":
                result.append(self.getGroupInfo(n))
        return result

    security.declareProtected(ModifyPortalContent, "deleteItems")
    def deleteItems(self, itemIds):
        """Delete the items with the given ids."""

        if itemIds:
            dom = minidom.parseString(str(self.body))
            document = dom.documentElement
            for itemId in itemIds:
                item = self.getItemById(document, itemId)
                if item is not None:
                    parent = item.parentNode
                    parent.removeChild(item)
            self.body = document.toxml()

    security.declareProtected(ViewQuestionnaire, "getQuestion")
    def getQuestion(self, questionId):
        """Return the information of the question with the given id."""

        dom = minidom.parseString(str(self.body))
        document = dom.documentElement
        question = self.getItemById(document, questionId)
        if question is None:
            return None
        return self.getQuestionInfo(question)

    security.declarePrivate("getQuestionInfo")
    def getQuestionInfo(self, question):
        """Return the information of the question with the given id."""

        dict = {}
        dict["type"] = "q"
        dict["id"] = question.getAttribute("id")

        text = self.getChildrenByTagName(question, "text")[0]
        dict["text"] = text.firstChild.nodeValue

        options = {}
        legends = self.getChildrenByTagName(question, "options")
        if legends:
            for option in self.getChildrenByTagName(legends[0], "option"):
                optionValue = option.getAttribute("value")
                options[optionValue] = option.firstChild.nodeValue

        sortedOptions = []
        for i in range(len(options)):
            sortedOptions.append(options[str(i+1)])
        dict['options'] = sortedOptions

        dict['scale'] = len(sortedOptions)

        if question.hasAttribute("answered"):
            dict["answered"] = int(question.getAttribute("answered"))

        if question.hasAttribute("average"):
            dict["average"] = float(question.getAttribute("average"))
        return dict

    security.declareProtected(ModifyPortalContent, "addQuestion")
    def addQuestion(self, text):
        """Add a question with the given text."""

        dom = minidom.parseString(str(self.body))
        document = dom.documentElement
        questionId = "q" + self.getNextId("question", document=document)
        questionAttrs = {"id": questionId}
        question = self.createChild(document, "question",
                                    attributes=questionAttrs)
        self.createChild(question, "text", text=text)
        self.body = document.toxml()
        return questionId

    security.declareProtected(ModifyPortalContent, "updateQuestion")
    def updateQuestion(self, questionId, text, options):
        """Update the information of the question with the given id."""

        dom = minidom.parseString(str(self.body))
        document = dom.documentElement
        question = self.getItemById(document, questionId)
        if question is not None:
            oldText = self.getChildrenByTagName(question, "text")[0]
            question.removeChild(oldText)
            self.createChild(question, "text", text=text.strip())

            oldOptionss = self.getChildrenByTagName(question, "options")
            if oldOptionss:
                question.removeChild(oldOptionss[0])
            i = 0
            if options.strip():
                newOptions = self.createChild(question, "options")
                for option in options.splitlines():
                    if option.strip():
                        i += 1
                        self.createChild(newOptions, "option",
                                         attributes={"value": str(i)},
                                         text=option)

            self.body = document.toxml()

    security.declarePrivate("getGroupInfo")
    def getGroupInfo(self, group):
        """Return the information of the given group element."""

        dict = {}
        dict["type"] = "g"
        dict["id"] = group.getAttribute("id")

        title = self.getChildrenByTagName(group, "title")[0]
        dict["title"] = title.firstChild.nodeValue

        dict["scale"] = int(group.getAttribute("scale"))

        options = {}
        legends = self.getChildrenByTagName(group, "legend")
        if legends:
            for option in self.getChildrenByTagName(legends[0], "option"):
                optionValue = option.getAttribute("value")
                options[optionValue] = option.firstChild.nodeValue

        sortedOptions = []
        for i in range(len(options)):
            sortedOptions.append(options[str(i+1)])
        dict["options"] = sortedOptions

        descriptions = self.getChildrenByTagName(group, "description")
        if not descriptions:
            dict["description"] = ""
        else:
            dict["description"] = descriptions[0].firstChild.nodeValue
        return dict

    security.declareProtected(ViewQuestionnaire, "getGroup")
    def getGroup(self, groupId):
        """Return the information of the group with the given id."""

        dom = minidom.parseString(str(self.body))
        document = dom.documentElement
        group = self.getItemById(document, groupId)
        if group is None:
            return None
        return self.getGroupInfo(group)

    security.declareProtected(ModifyPortalContent, "addGroup")
    def addGroup(self, title, scale):
        """Add a group with the given title and scale."""

        dom = minidom.parseString(str(self.body))
        document = dom.documentElement
        groupId = "g" + self.getNextId("group", document=document)
        groupAttrs = {"id": groupId, "scale": str(scale)}
        group = self.createChild(document, "group", attributes=groupAttrs)
        self.createChild(group, "title", text=title)
        self.body = document.toxml()
        return groupId

    security.declareProtected(ModifyPortalContent, "updateGroup")
    def updateGroup(self, groupId, title, scale, legend, description):
        """Update the information of the group with the given id."""

        dom = minidom.parseString(str(self.body))
        document = dom.documentElement
        group = self.getItemById(document, groupId)
        if group is not None:
            oldTitle = self.getChildrenByTagName(group, "title")[0]
            group.removeChild(oldTitle)
            self.createChild(group, "title", text=title.strip())

            group.setAttribute("scale", str(scale))

            oldLegends = self.getChildrenByTagName(group, "legend")
            if oldLegends:
                group.removeChild(oldLegends[0])
            if legend.strip():
                newLegend = self.createChild(group, "legend")
                i = 0
                for option in legend.splitlines():
                    i += 1
                    if i > scale:
                        break
                    if option.strip():
                        self.createChild(newLegend, "option",
                                         attributes={"value": str(i)},
                                         text=option)

            # create a new description element and replace the old one
            oldDescriptions = self.getChildrenByTagName(group, "description")
            if oldDescriptions:
                group.removeChild(oldDescriptions[0])
            if description.strip():
                self.createChild(group, "description", text=description.strip())

            self.body = document.toxml()

    security.declareProtected(ViewQuestionnaire, "getQuestionsInGroup")
    def getQuestionsInGroup(self, groupId):
        """Return all questions in the group with the given id."""

        result = []
        dom = minidom.parseString(str(self.body))
        document = dom.documentElement
        group = self.getItemById(document, groupId)
        if group is not None:
            questions = self.getChildrenByTagName(group, "question")
            for question in questions:
                result.append(self.getQuestionInfo(question))
        return result

    security.declareProtected(ModifyPortalContent, "addQuestionToGroup")
    def addQuestionToGroup(self, groupId, question):
        """Add a question to the group with the given id."""

        dom = minidom.parseString(str(self.body))
        document = dom.documentElement
        group = self.getItemById(document, groupId)
        if group is not None:
            questionId = "q" + self.getNextId("question", document=document)
            q = self.createChild(group, "question",
                                 attributes={"id": questionId})
            self.createChild(q, "text", text=question)
            self.body = document.toxml()

    security.declareProtected(ViewQuestionnaire, "isOpen")
    def isOpen(self):
        wt = getToolByName(self, "portal_workflow")
        rs = wt.getInfoFor(self, "review_state")
        if not (rs == "published"):
            return False

        effective = self.EffectiveDate()
        expired = self.ExpirationDate()
        now = DateTime()

        if effective is None:
            isStarted = True
        else:
            isStarted = (now >= DateTime(effective))

        if str(expired) == "None":
            isNotOver = True
        else:
            isNotOver = (now <= DateTime(expired))
        return isStarted and isNotOver

    security.declareProtected(ViewQuestionnaireResults, "getTickets")
    def getTickets(self):
        """Return unused tickets."""

        if not hasattr(self, "tickets"):
            return []
        return list(self.tickets)

    security.declareProtected(ViewQuestionnaireResults, "getUsedTickets")
    def getUsedTickets(self):
        """Return used tickets."""

        if not hasattr(self, "used_tickets"):
            return []
        return list(self.used_tickets)

    security.declareProtected(ViewQuestionnaire, "getSubmittedCount")
    def getSubmittedCount(self):
        """Return number of used tickets."""

        if not hasattr(self, "used_tickets"):
            return 0
        return len(self.used_tickets)

    security.declareProtected(ViewQuestionnaire, "checkTicket")
    def checkTicket(self, ticket):
        """Return whether the given ticket is valid or not."""

        if hasattr(self, "used_tickets"):
            if ticket in self.used_tickets:
                return False
        if self.use_ticket:
            if hasattr(self, "tickets"):
                return ticket in self.tickets
            else:
                return False
        return True

    security.declarePrivate("createRandomTicket")
    def createRandomTicket(self, size=10):
        """Create a random ticket which consists of a number of integers."""

        digits = [str(random.randrange(0, 10)) for i in xrange(size)]
        return "".join(digits)

    security.declarePrivate("addTicket")
    def addTicket(self, ticket):
        """Add a ticket to unused tickets."""

        if not hasattr(self, "tickets"):
            self.tickets = PersistentList()
        if not hasattr(self, "used_tickets"):
            self.used_tickets = PersistentList()
        if (not (ticket in self.tickets)) and \
           (not (ticket in self.used_tickets)):
            self.tickets.append(ticket)

    security.declareProtected(ModifyPortalContent, "createTickets")
    def createTickets(self, count=1):
        """Create a number of random tickets. Return the created number."""

        for i in xrange(count):
            self.addTicket(self.createRandomTicket())
        return count

    security.declareProtected(ModifyPortalContent, "deleteAllTickets")
    def deleteAllTickets(self):
        """Delete all unused tickets."""

        self.tickets = PersistentList()

    security.declareProtected(FilloutQuestionnaire, "fillout")
    def fillout(self, ticket, request):
        """Save a submitted questionnaire."""

        if self.checkTicket(ticket):
            dom = minidom.parseString(str(self.body))
            document = dom.documentElement
            adom = minidom.parseString(str(self.answers))
            adocument = adom.documentElement
            ae = self.createChild(adocument, "form", attributes={"id": ticket})
            for question in document.getElementsByTagName("question"):
                questionId = question.getAttribute("id")
                if request.has_key(questionId):
                    self.createChild(ae, "question",
                                     attributes={"id": str(questionId)},
                                     text=request[questionId])

            if request.has_key("comment"):
                comment = request.comment.strip()
                if comment:
                    self.createChild(ae, "comment", text=comment)

            if not hasattr(self, "used_tickets"):
                self.used_tickets = PersistentList()
            self.used_tickets.append(ticket)

            if hasattr(self, "tickets"):
                if ticket in self.tickets:
                    self.tickets.remove(ticket)

            self.answers = adocument.toxml()
            self.needsUpdate = True

    security.declareProtected(ViewQuestionnaire, "getAnswer")
    def getAnswer(self, ticket, questionId, adocument=None):
        """
        Return the answer for the question with the given id in the form
        speficied by the ticket.
        """

        if not _checkPermission(ViewQuestionnaireResults, self):
            return None

        if ticket:
            if adocument is None:
                adom = minidom.parseString(str(self.answers))
                adocument = adom.documentElement
            form = self.getItemById(adocument, ticket, tagName="form")
            if form is not None:
                for question in self.getChildrenByTagName(form, "question"):
                    if question.getAttribute('id') == questionId:
                        return int(question.firstChild.nodeValue)
        return None

    security.declareProtected(ViewQuestionnaire, "getComment")
    def getComment(self, ticket, adocument=None):
        """Return the comment in the form speficied by the ticket."""

        if not _checkPermission(ViewQuestionnaireResults, self):
            return ""
        if ticket:
            if adocument is None:
                adom = minidom.parseString(str(self.answers))
                adocument = adom.documentElement
            form = self.getItemById(adocument, ticket, tagName="form")
            if form is not None:
                comments = self.getChildrenByTagName(form, "comment")
                if comments:
                    return comments[0].childNodes[0].nodeValue
        return ''

    security.declareProtected(ModifyPortalContent, "deleteForms")
    def deleteForms(self, formIds):
        """Delete the submitted forms with the given ids."""

        if formIds:
            adom = minidom.parseString(str(self.answers))
            adocument = adom.documentElement
            for formId in formIds:
                form = self.getItemById(adocument, formId, tagName="form")
                if form is not None:
                    parent = form.parentNode
                    parent.removeChild(form)
                    self.used_tickets.remove(formId)
            self.answers = adocument.toxml()
            self.needsUpdate = True

    security.declarePrivate("getAnswersByQuestionId")
    def getAnswersByQuestionId(self, questionId, adocument=None):
        """
        Return the answers in all submitted forms for the question with the
        given id.
        """

        if adocument is None:
            adom = minidom.parseString(str(self.answers))
            adocument = adom.documentElement
        answers = []
        for question in adocument.getElementsByTagName("question"):
            if question.getAttribute("id") == questionId:
                answer = int(question.firstChild.nodeValue)
                answers.append(answer)
        return answers

    security.declarePrivate("generateSummary")
    def generateSummary(self, document=None, adocument=None):
        """
        Update the questionnaire information to reflect the answer counts and
        percentages for each answer to each question.
        """

        if document is None:
            dom = minidom.parseString(str(self.body))
            document = dom.documentElement

        if adocument is None:
            adom = minidom.parseString(str(self.answers))
            adocument = adom.documentElement

        for question in document.getElementsByTagName("question"):
            questionId = question.getAttribute("id")

            summary = {}
            answered = 0
            for answer in self.getAnswersByQuestionId(questionId,
                                                      adocument=adocument):
                if answer:
                    answered += 1
                if not summary.has_key(answer):
                    summary[answer] = 1
                else:
                    summary[answer] += 1

            # compute the weighted average
            average = 0
            answer_total = 0
            for answer in summary.keys():
                answer_total += int(answer) * summary[answer]
            if answer_total > 0:
                average = round(float(answer_total)/answered, 2)

            question.setAttribute("answered", str(answered))
            question.setAttribute("average", str(average))

            # delete the old answer summaries first
            oldAnswers = self.getChildrenByTagName(question, "answer")
            for oldAnswer in oldAnswers:
                question.removeChild(oldAnswer)

            # append the new answer summaries
            for answer in summary.keys():
                attrs = {"count": str(summary[answer])}
                if answer:
                    attrs["percent"] = str(100*summary[answer]/answered)
                self.createChild(question, "answer", attributes=attrs,
                                 text=str(answer))

        self.body = document.toxml()

    security.declareProtected(ViewQuestionnaireResults, "evaluate")
    def evaluate(self):
        """Return the evaluation results."""

        if not hasattr(self, "needsUpdate"):
            self.needsUpdate = True

        dom = minidom.parseString(str(self.body))
        document = dom.documentElement

        adom = minidom.parseString(str(self.answers))
        adocument = adom.documentElement

        if self.needsUpdate:
            self.generateSummary(document=document, adocument=adocument)
            self.needsUpdate = False

        result = []
        for question in document.getElementsByTagName("question"):
            dict = self.getQuestionInfo(question)

            parent = question.parentNode
            if parent.tagName == "group":
                groupInfo = self.getGroupInfo(parent)
                dict["scale"] = groupInfo["scale"]
                dict["options"] = groupInfo["options"]

            summary = []
            for i in xrange(dict["scale"]):
                summary.append((0, 0))
            answers = self.getChildrenByTagName(question, "answer")
            for answer in answers:
                answerValue = int(answer.firstChild.nodeValue)
                if answerValue > 0:
                    answerCount = int(answer.getAttribute("count"))
                    answerPerCent = int(answer.getAttribute("percent"))
                    summary[answerValue-1] = (answerCount, answerPerCent)
            dict["answers"] = summary

            result.append(dict)
        return result

    security.declareProtected(ViewQuestionnaireResults, "getComments")
    def getComments(self):
        """Return all comments."""

        adom = minidom.parseString(str(self.answers))
        adocument = adom.documentElement
        result = []
        for comment in adocument.getElementsByTagName("comment"):
            if comment.firstChild.nodeValue:
                dict = {}
                dict["id"] = comment.parentNode.getAttribute("id")
                dict["text"] = comment.firstChild.nodeValue
                result.append(dict)
        return result

    security.declareProtected(ViewQuestionnaireResults, "isPDFAvailable")
    def isPDFAvailable(self):
        """Return whether generation of PDF reports are available."""

        return pdfAvailable

    security.declareProtected(ViewQuestionnaireResults, "getPDFReport")
    def getPDFReport(self):
        """Return a PDF report of the results."""

        if pdfAvailable:
            pdfBaseDir = os.path.join(Globals.INSTANCE_HOME, "var",
                                      "questionnaires")
            try:
                os.makedirs(pdfBaseDir)
            except OSError:
                pass

            pdfFileName = os.path.join(pdfBaseDir, "%s.pdf" % self.id)
            pdfReport = canvas.Canvas(pdfFileName, pagesize=A4)
            pdfReport.setTitle(self.title)
            pdfReport.setAuthor("CMFQuestionnaire")

            curX, curY = self.putPDFText(pdfReport, self.title,
                                         self.leftX, self.topY, fontSize=20)

            submitCount = len(self.used_tickets)
            curX, curY = self.putPDFText(pdfReport,
                                         _(u"Total submissions") + ": " + str(submitCount),
                                         curX, curY, font="Serif-Italic")

            valueStep = 1
            if submitCount > 10:
                valueStep = 5
            if submitCount > 50:
                valueStep = 10
            if submitCount > 100:
                valueStep = 50

            results = self.evaluate()
            for result in results:
                lines = 1 + (len(self.title)/100)
                height = lines * 12 + self.chartY + 20
                if curY - height < self.limitY:
                    pdfReport.showPage()
                    curX, curY = self.leftX, self.topY

                pdfReport.line(self.leftX, curY, self.limitX, curY)
                curX, curY = self.putPDFText(pdfReport, result['text'],
                                             self.leftX, curY - 20)

                barChart = VerticalBarChart()
                barChart.valueAxis.valueMin = 0
                barChart.valueAxis.valueMax = submitCount + 1
                barChart.valueAxis.valueStep = valueStep

                barChart.categoryAxis.categoryNames = []
                barChart.data = []
                values = []
                i = 0
                for answer in result["answers"]:
                    i += 1
                    barChart.categoryAxis.categoryNames.append(str(i))
                    values.append(answer[0])
                barChart.data.append(values)

                barChart.x = 20
                barChart.y = 20
                barChart.width = 100
                barChart.height = 100

                pieChart = Pie()
                pieChart.labels = barChart.categoryAxis.categoryNames
                pieChart.data = []
                for answer in result["answers"]:
                    pieChart.data.append(answer[1])

                pieChart.x = barChart.x + barChart.width + 30
                pieChart.y = barChart.y - 10
                pieChart.width = 100
                pieChart.height = 100

                chart = Drawing(self.chartX, self.chartY)
                chart.add(barChart)
                chart.add(pieChart)

                nextY = curY - self.chartY + 10
                chart.drawOn(pdfReport, self.leftX, nextY)

                curX, curY = self.putPDFText(pdfReport,
                    _(u"Answer count") + ": " + str(result["answered"]),
                    self.leftX + self.chartX + 10, curY - 10,
                    font="Serif-Italic", fontSize=10)

                curX, curY = self.putPDFText(pdfReport,
                    _(u"Average") + ": " + str(result["average"]),
                    self.leftX + self.chartX + 10, curY - 10,
                    font="Serif-Italic", fontSize=10)
                curY = curY - 10

                legend = result["options"]
                for i in xrange(len(legend)):
                    curX, curY = self.putPDFText(pdfReport,
                        "%d: %s" % (i+1, legend[i]),
                        self.leftX + self.chartX + 10, curY,
                        font="Serif-Italic", fontSize=10)

                curX, curY = self.leftX, nextY - 20

            pdfReport.showPage()

            curX, curY = self.putPDFText(pdfReport, _(u"Comments"),
                                         self.leftX, self.topY, fontSize=20)
            for comment in self.getComments():
                commentText = comment["text"]
                # estimate a height and check whether we should start a new page
                lines = 1 + (len(commentText) / 100)
                height = lines * 12 + 20
                if curY - height < self.limitY:
                    pdfReport.showPage()
                    curX, curY = self.leftX, self.topY
                pdfReport.line(self.leftX, curY, self.limitX, curY)
                curX, curY = self.putPDFText(pdfReport, commentText,
                                             self.leftX, curY - 20)

            pdfReport.showPage()
            pdfReport.save()

            pdfFile = open(pdfFileName)
            pdfString = StringIO(pdfFile.read())
            pdfFile.close()
            return pdfString.read()

    security.declarePrivate("putPDFText")
    def putPDFText(self, pdfReport, text, curX, curY, limitX=None, limitY=None,
                    font='Serif', fontSize=12):
        """Output some text to the PDF report."""

        if limitX == None:
            limitX = self.limitX
        if limitY == None:
            limitY = self.limitY
        tmpText = canvas.textobject.PDFTextObject(pdfReport, x=curX, y=curY)
        pdfText = canvas.textobject.PDFTextObject(pdfReport, x=curX, y=curY)
        tmpText.setFont(font, fontSize)
        pdfText.setFont(font, fontSize)
        for word in text.split(' '):
            if word.strip():
                tmpText.textOut(word + ' ')
                if tmpText.getX() > limitX:
                    pdfText.textLine('')
                    pdfText.textOut(word + ' ')
                    tmpText.textLine('')
                    tmpText.textOut(word + ' ')
                else:
                    pdfText.textOut(word + ' ')
        pdfText.textLine('')
        curX, curY = pdfText.getX(), pdfText.getY()
        pdfReport.drawText(pdfText)
        return curX, curY

    security.declareProtected(ViewQuestionnaireResults, "getXMLDump")
    def getXMLDump(self):
        """Return an XML text containing all questionnaire data."""

        dom = minidom.parseString(str(self.body))
        document = dom.documentElement

        adom = minidom.parseString(str(self.answers))
        adocument = adom.documentElement

        document.appendChild(adocument)
        return document.toprettyxml()

    security.declareProtected(ViewQuestionnaireResults, "getCSVDump")
    def getCSVDump(self):
        """Return a CSV text containing all questionnaire data."""

        dom = minidom.parseString(str(self.body))
        document = dom.documentElement

        adom = minidom.parseString(str(self.answers))
        adocument = adom.documentElement

        questions = document.getElementsByTagName("question")
        questionIds = [q.getAttribute("id") for q in questions]
        csvString = "Id,%s\n" % ','.join(questionIds)
        for ticket in self.used_tickets:
            csvString += ticket
            for questionId in questionIds:
                answer = self.getAnswer(ticket, questionId, adocument=adocument)
                if answer:
                    csvString += ",%d" % answer
                else:
                    csvString += ","
            csvString += "\n"
        return csvString

    security.declareProtected(ViewQuestionnaireResults, "isXLSAvailable")
    def isXLSAvailable(self):
        """Return whether generation of Excel dumps are available."""

        return xlsAvailable

    security.declareProtected(ViewQuestionnaireResults, "getExcelDump")
    def getExcelDump(self):
        """Return an Excel file containing all questionnaire data."""

        if xlsAvailable:
            return ""


registerATCT(Questionnaire, PROJECTNAME)
