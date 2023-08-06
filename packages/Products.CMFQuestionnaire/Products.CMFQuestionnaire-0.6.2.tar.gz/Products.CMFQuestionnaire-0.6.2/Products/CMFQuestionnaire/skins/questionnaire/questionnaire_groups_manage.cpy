## Controller Python Script "questionnaire_groups_manage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=groupId='',newTitle='',newScale='',newLegend='',newDescription='',question='',questionIds=''
##title=Manage a question group in a questionnaire

from Products.CMFQuestionnaire import QuestionnaireMessageFactory as _

state.setNextAction("redirect_to:string:questionnaire_design_form")
button = context.REQUEST.controller_state.button

if button == "updateGroup":
    context.updateGroup(groupId, newTitle, newScale, newLegend, newDescription)
    context.plone_utils.addPortalMessage(_(u"Group information updated."))
    state.setNextAction("redirect_to:string:questionnaire_group_form?groupId=%s" % groupId)
elif button == "addQuestion":
    context.addQuestionToGroup(groupId, question)
    context.plone_utils.addPortalMessage(_(u"Question added."))
    state.setNextAction("redirect_to:string:questionnaire_group_form?groupId=%s" % groupId)
elif button == "deleteQuestions":
    context.deleteItems(questionIds)
    context.plone_utils.addPortalMessage(_(u"Questions deleted."))
    state.setNextAction("redirect_to:string:questionnaire_group_form?groupId=%s" % groupId)
else:
    context.plone_utils.addPortalMessage(_(u"Unknown operation."))
    state.setNextAction("redirect_to:string:questionnaire_design_form")

return state.set(context=context)
