## Controller Python Script "registrant_post"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Finalize posting of an issue
##

from Products.CMFCore.utils import getToolByName

# Ensure only manager can edit/delete the response from now on
portal_workflow = getToolByName(context, 'portal_workflow')
portal_membership = getToolByName(context, 'portal_membership')

if portal_membership.isAnonymousUser():
    context.setCreators(('(anonymous)',))

# Compute thank you message before transition until anonymous has permission to access registrant object, 
# because anonymous will have no access to registrant object later
kw = {}
kw['registrant'] = context
text = context.aq_parent.getThankYouText(**kw)
context.REQUEST.SESSION.set('signupsheet.thankyoutext', text)

#if it is a new posting, then follow the workflow that transitions the state and provides for a thank you message
#otherwise return to the view mode for cases when manager needs to update registrant info
#code adapted from Andreas Jung's branch
current_state = context.portal_workflow.getInfoFor(context, 'review_state')
posted = False
if current_state in ('new', ):
    posted = True
    portal_workflow.doActionFor(context, 'post')

if posted:
    state.setNextAction('redirect_to:string:${folder_url}/thank_you_message')
else:
    state.setNextAction('redirect_to:string:view')


return state
