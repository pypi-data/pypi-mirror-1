## Controller Python Script "questionnaire_form_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=formIds=''
##title=Delete submitted forms from a questionnaire
##

from Products.CMFQuestionnaire import QuestionnaireMessageFactory as _

context.deleteForms(formIds)
context.plone_utils.addPortalMessage(_(u"Forms deleted."))
state.setNextAction("redirect_to:string:questionnaire_submissions_form")
return state.set(context=context)
