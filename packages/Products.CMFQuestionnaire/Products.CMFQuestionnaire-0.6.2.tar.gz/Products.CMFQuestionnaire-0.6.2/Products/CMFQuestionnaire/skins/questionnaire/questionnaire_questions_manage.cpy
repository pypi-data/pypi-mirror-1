## Controller Python Script "questionnaire_questions_manage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=questionId='',newText='',newOptions=''
##title=Manage a question group in a questionnaire

from Products.CMFQuestionnaire import QuestionnaireMessageFactory as _

state.setNextAction("redirect_to:string:questionnaire_design_form")
button = context.REQUEST.controller_state.button

if button == "updateQuestion":
    context.updateQuestion(questionId, newText, newOptions)
    context.plone_utils.addPortalMessage(_(u"Question updated."))
    state.setNextAction("redirect_to:string:questionnaire_question_form?questionId=%s" % questionId)
else:
    context.plone_utils.addPortalMessage(_(u"Unknown operation."))
    state.setNextAction("redirect_to:string:questionnaire_design_form")

return state.set(context=context)
