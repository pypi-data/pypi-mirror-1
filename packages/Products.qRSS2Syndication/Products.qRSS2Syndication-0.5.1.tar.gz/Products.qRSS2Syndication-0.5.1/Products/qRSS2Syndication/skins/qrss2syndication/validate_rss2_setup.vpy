## Controlled Python Script "validate_rss2_setup"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates an email
##
articles_number = context.REQUEST.get('articles_number')
try:
  z = int(articles_number)
except:
    state.setError('articles_number', 'The articles number value should be integer')
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
return state


