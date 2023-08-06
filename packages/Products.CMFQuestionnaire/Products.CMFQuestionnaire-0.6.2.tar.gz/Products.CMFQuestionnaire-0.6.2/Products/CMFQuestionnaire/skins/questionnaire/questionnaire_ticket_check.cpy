## Controller Python Script "questionnaire_ticket_check"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ticket=''
##title=Check whether the given ticket is valid for the questionnaire
##

from Products.CMFQuestionnaire import QuestionnaireMessageFactory as _

state.setNextAction("traverse_to:string:questionnaire_view_form")

valid = context.checkTicket(ticket)
if not valid:
    context.plone_utils.addPortalMessage(_(u"Not a valid ticket."))

return state.set(context=context)
