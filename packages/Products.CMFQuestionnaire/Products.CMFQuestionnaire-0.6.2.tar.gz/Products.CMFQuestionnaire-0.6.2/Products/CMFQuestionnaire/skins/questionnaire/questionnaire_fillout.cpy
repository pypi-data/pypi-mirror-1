## Controller Python Script "questionnaire_fillout"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ticket=''
##title=Fill out a questionnaire
##

from DateTime import DateTime
from Products.CMFQuestionnaire import QuestionnaireMessageFactory as _

state.setNextAction("traverse_to:string:questionnaire_view_form")

if not context.use_ticket:
    ticket = context.portal_membership.getAuthenticatedMember().getId()
    if not ticket:
        ipaddress = context.REQUEST.getClientAddr()
        now = DateTime()
        ticket = "%s-%s" % (ipaddress, now)

valid = context.checkTicket(ticket)
if valid:
    context.fillout(ticket, context.REQUEST)
    context.plone_utils.addPortalMessage(_(u"Your answers have been submitted."))
else:
    context.plone_utils.addPortalMessage(_(u"Not a valid ticket."))

return state.set(context=context)
