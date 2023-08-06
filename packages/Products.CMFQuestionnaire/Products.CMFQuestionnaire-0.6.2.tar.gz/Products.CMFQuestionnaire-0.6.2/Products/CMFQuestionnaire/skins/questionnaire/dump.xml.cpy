## Controller Python Script "dump.xml"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Get all questionnaire data in XML format
##

context.REQUEST.RESPONSE.setHeader("Content-Type", "text/xml")
return context.getXMLDump()
