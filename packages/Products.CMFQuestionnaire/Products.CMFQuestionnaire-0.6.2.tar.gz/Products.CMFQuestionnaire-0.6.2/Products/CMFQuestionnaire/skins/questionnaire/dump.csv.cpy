## Controller Python Script "dump.csv"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Get all questionnaire data in CSV format
##

context.REQUEST.RESPONSE.setHeader("Content-Type", "text/plain")
return context.getCSVDump()
