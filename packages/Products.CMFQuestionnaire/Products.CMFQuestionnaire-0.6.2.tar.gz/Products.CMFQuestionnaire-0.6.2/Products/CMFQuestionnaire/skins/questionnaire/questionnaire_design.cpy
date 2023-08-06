## Controller Python Script "questionnaire_design"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=itemIds=''
##title=Design a questionnaire

from Products.CMFQuestionnaire import QuestionnaireMessageFactory as _

state.setNextAction("redirect_to:string:questionnaire_design_form")
button = context.REQUEST.controller_state.button

if button == "addGroup":
    groupId = context.addGroup(_(u"New Group"), "3")
    state.setNextAction("redirect_to:string:questionnaire_group_form?groupId=%s" % groupId)
elif button == "addQuestion":
    questionId = context.addQuestion(_(u"New Question"))
    state.setNextAction("redirect_to:string:questionnaire_question_form?questionId=%s" % questionId)
elif button == "deleteItems":
    context.deleteItems(itemIds)
    context.plone_utils.addPortalMessage(_(u"Items deleted."))
    state.setNextAction("redirect_to:string:questionnaire_design_form")
else:
    context.plone_utils.addPortalMessage(_(u"Unknown operation."))
    state.setNextAction("redirect_to:string:questionnaire_design_form")

return state.set(context=context)
