## Controller Python Script "dump.xls"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Get all questionnaire data in Excel format
##

context.REQUEST.RESPONSE.setHeader("Content-Type", "application/msexcel")
return context.getExcelDump()
