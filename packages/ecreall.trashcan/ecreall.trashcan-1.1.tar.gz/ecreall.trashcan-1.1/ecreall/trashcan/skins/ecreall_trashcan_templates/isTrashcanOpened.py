## Script (Python) "isTrashcanOpened"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=

return context.REQUEST.SESSION.get('trashcan', False)
