## Controller Python Script "report.pdf"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Get the PDF report of questionnaire results
##

context.REQUEST.RESPONSE.setHeader('Content-Type', 'application/pdf')
return context.getPDFReport()
