## Script (Python) "Validate page ecards" 
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=email_body='', sender_name='', sender_email='', recipient_name='', recipient_email='', image_id
##title=Validates content publishing
##

def validateEmail(email):
    return context.plone_utils.validateSingleEmailAddress(email)

if not email_body.strip():
    state.setError('email_body', 'Email text is empty')

if not sender_name:
    state.setError('sender_name', 'No sender email given')

if not sender_email:
    state.setError('sender_email', 'No sender email given')

if not recipient_name:
    state.setError('recipient_name', 'No recipient name given')

if not recipient_email:
    state.setError('recipient_email', 'No recipient email given')

if not validateEmail(sender_email):
    state.setError('sender_email', 'Invalid email address: %s' % sender_email)
    
if not validateEmail(recipient_email):
    state.setError('recipient_email', 'Invalid email address: %s' % recipient_email)

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the following errors first.', image_id=image_id)
else:
    return state
