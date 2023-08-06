from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

def _getAllValidEmailsFromGroup(putils, acl_users, group):
    """Look at every user in the group, return all valid emails"""
    return [m.getProperty('email') for m in group.getGroupMembers() if putils.validateSingleEmailAddress(m.getProperty('email'))]

def _getSendToValues(object):
    """Load the portal configuration for the notify system and obtain a list of emails.
    If the sendto_all is True, the mail will be sent to all members of the Plone site.
    The sendto_values value is used to look for name of groups, then name on users in the portal and finally for normal emails.
    @return a list of emails
    """
    ploneboard_notify_properties = getToolByName(object,'portal_properties')['ploneboard_notify_properties']
    sendto_all = ploneboard_notify_properties.sendto_all
    sendto_values = ploneboard_notify_properties.sendto_values
    acl_users = getToolByName(object, 'acl_users')
    putils = getToolByName(object, 'plone_utils')

    emails = []
    if sendto_all:
        users = acl_users.getUsers()
        emails.extend([m.getProperty('email') for m in users if putils.validateSingleEmailAddress(m.getProperty('email'))])
    for entry in sendto_values:
        group = acl_users.getGroupById(entry)
        # 1 - is a group?
        if group:
            emails.extend(_getAllValidEmailsFromGroup(putils, acl_users, group))
            continue
        # 2 - is a member?
        user = acl_users.getUserById(entry)
        if user:
            email = user.getProperty('email')
            if putils.validateSingleEmailAddress(email):
                emails.append(email)
            continue
        # 3 - is a valid email address?
        if putils.validateSingleEmailAddress(entry):
            emails.append(entry)

    return emails

def sendMail(object, event):
    """A Zope3 event for sending emails"""
    ploneboard_notify_properties = getToolByName(object,'portal_properties')['ploneboard_notify_properties']
    debug_mode = ploneboard_notify_properties.debug_mode
    portal = getToolByName(object,"portal_url").getPortalObject()
    portal_transforms = getToolByName(object, "portal_transforms")

    send_from = portal.getProperty('email_from_address')
    if type(send_from)==tuple and send_from:
        send_from = send_from[0]
       
    send_to = _getSendToValues(object)
    
    translation_service = getToolByName(object,'translation_service')
    
    msg_sbj = u"New message added on the forum "
    subject = translation_service.utranslate(domain='Products.PloneboardNotify',
                                             msgid=msg_sbj,
                                             default=msg_sbj,
                                             context=object)
    subject+= object.aq_parent.Title().decode('utf-8')

    msg_txt = u"The new message is:"
    text = translation_service.utranslate(domain='Products.PloneboardNotify',
                                          msgid=msg_txt,
                                          default=msg_txt,
                                          context=object)
    
    data_body_to_plaintext = portal_transforms.convert("html_to_web_intelligent_plain_text", object.REQUEST.form['text'])
    body_to_plaintext = data_body_to_plaintext.getData()
    
    text += "\n\n" + body_to_plaintext.decode('utf-8')
    text += "\n\n" + object.absolute_url()
    
    mail_host = getToolByName(object, 'MailHost')

    try:
        if debug_mode:
            object.plone_log("Notification from message subject: %s" % subject.encode('iso-8859-1'))
            object.plone_log("Notification from message text: %s" % text.encode('iso-8859-1'))
            object.plone_log("Notification from message %s sent to %s" % (object.absolute_url_path(), ",".join(send_to)))
        else:
            mail_host.secureSend(text.encode('iso-8859-1'), mto=[], mfrom=send_from,
                                 subject=subject.encode('iso-8859-1'),
                                 encode="utf-8", mbcc=send_to)
    except Exception, inst:
        putils = getToolByName(object,'plone_utils')
        putils.addPortalMessage('Not able to send notifications', type='warning')
        object.plone_log(str(inst))



