## Script (Python) "ecardsuccess"
##bind container=container
##bind context=context
##bind namespace=
##bind state=state
##bind subpath=traverse_subpath
##parameters=self
##title=used to post form values for sending via email
##

# get our view, request
popup_view = context.restrictedTraverse('@@ecardpopup_browserview')
request = container.REQUEST

# Generate the message
sender_name = request.form['sender_first_name'] + ' ' + request.form['sender_last_name']
to_name = request.form['friend_first_name'] + ' ' + request.form['friend_last_name']
subject = "%s %s" % (request.form['sender_first_name'].strip(),
                     popup_view.stripNewLines(request.form['subject'].strip()),)
send_to_address = popup_view.stripNewLines(request.form['send_to_address'])
send_from_address = popup_view.stripNewLines(request.form['send_from_address'])

full_to_address = '"%(to_name)s" <%(send_to_address)s>' % {
                            'to_name':popup_view.stripNewLines(to_name),
                            'send_to_address': send_to_address,}

full_from_address = '"%(sender_name)s" <%(send_from_address)s>' % {
    'sender_name':popup_view.stripNewLines(sender_name),
    'send_from_address': send_from_address,
}

# setup the message body
options = {
    'subject': subject,
    'friend_first_name': request.form['friend_first_name'],
    'comment': context.portal_transforms.convert('text_to_html', request.form['comment']),
    'sender_first_name': request.form['sender_first_name'],
    'credits':request.form['credits'],
    'emailAppendedMessage':request.form['emailAppendedMessage'],
    'image_url':request.form['image_url'],
}

# Send the eCard to friend with the method on our popup view
popup_view.sendECard(
    message = context.email_template(**options),
    full_to_address = full_to_address,
    full_from_address = full_from_address,
    subject = subject)

# Always make sure to return the ControllerState object
return state
