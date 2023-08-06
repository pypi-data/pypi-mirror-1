## Script (Python) "onlinetest_getquestionlist"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from ZTUtils import LazyFilter

types = ('Question', )
states = ('published',)
ids = []

# extract the available list of questions
raw_items = context.contentValues(filter={'portal_type':  types,
                                      'review_state': states})
items = LazyFilter( raw_items, skip='View' )

for item in items:
    ids.append(item['id'])

return ids
