## Controller Python Script "questionnaire_tickets_manage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ticketCount=''
##title=Create, list and delete tickets for a questionnaire
##

from Products.CMFQuestionnaire import QuestionnaireMessageFactory as _

button = context.REQUEST.controller_state.button

if button == "createTickets":
    if ticketCount:
        ticketCount = int(ticketCount)
        if ticketCount > 0:
            count = context.createTickets(ticketCount)
            context.plone_utils.addPortalMessage(str(count) + " " + _(u"tickets created."))
elif button == "deleteAllTickets":
    context.deleteAllTickets()
    context.plone_utils.addPortalMessage(_(u"All tickets deleted."))
else:
    context.plone_utils.addPortalMessage(_(u"Unknown operation."))

state.setNextAction("redirect_to:string:questionnaire_submissions_form")
return state.set(context=context)
