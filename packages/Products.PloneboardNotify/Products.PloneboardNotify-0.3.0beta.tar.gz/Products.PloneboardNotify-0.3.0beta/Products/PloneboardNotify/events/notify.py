# -*- coding: utf-8 -*-

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

from zope import interface
from Products.PloneboardNotify.interfaces import ILocalBoardNotify

def _getAllValidEmailsFromGroup(putils, acl_users, group):
    """Look at every user in the group, return all valid emails"""
    return [m.getProperty('email') for m in group.getGroupMembers() if putils.validateSingleEmailAddress(m.getProperty('email'))]

def _getConfiguration(object):
    """Return the local or global configuration settings for notify"""
    # BBB: the best is to refactor this using adapters
    if not ILocalBoardNotify.providedBy(object):
        ploneboard_notify_properties = getToolByName(object,'portal_properties')['ploneboard_notify_properties']
        sendto_all = ploneboard_notify_properties.sendto_all
        sendto_values = ploneboard_notify_properties.sendto_values
    else:
        # Local configuration
        sendto_all = object.getProperty('forum_sendto_all', False)
        sendto_values = object.getProperty('forum_sendto_values', [])
    return sendto_all, sendto_values


def _getSendToValues(object):
    """Load the portal configuration for the notify system and obtain a list of emails.
    If the sendto_all is True, the mail will be sent to all members of the Plone site.
    The sendto_values value is used to look for name of groups, then name on users in the portal and finally for normal emails.
    @return a tuple with (cc emails, bcc emails) inside
    """
    sendto_all, sendto_values = _getConfiguration(object)
    acl_users = getToolByName(object, 'acl_users')
    mtool = getToolByName(object, 'portal_membership')
    putils = getToolByName(object, 'plone_utils')

    emails = []
    emails_bcc = []
    if sendto_all:
        users = acl_users.getUsers()
        emails_bcc.extend([m.getProperty('email') for m in users if putils.validateSingleEmailAddress(m.getProperty('email'))])
    for entry in sendto_values:
        if entry.startswith("#"):
            # I also support comment inside the emails data
            continue
        inBcc = False
        if entry.endswith("|bcc") or entry.endswith("|BCC"):
            entry = entry[:-4]
            inBcc = True 
        group = acl_users.getGroupById(entry)
        # 1 - is a group?
        if group:
            if inBcc:
                emails_bcc.extend(_getAllValidEmailsFromGroup(putils, acl_users, group))
            else:
                emails.extend(_getAllValidEmailsFromGroup(putils, acl_users, group))                
            continue
        # 2 - is a member?
        #user = acl_users.getUserById(entry) # BBB: seems not working... only on Plone 2.5?
        user = mtool.getMemberById(entry)
        if user:
            email = user.getProperty('email')
            if putils.validateSingleEmailAddress(email):
                if inBcc:
                    emails_bcc.append(email)
                else:
                    emails.append(email)
            continue
        # 3 - is a valid email address?
        if putils.validateSingleEmailAddress(entry):
            if inBcc:
                emails_bcc.append(entry)
            else:
                emails.append(entry)                
            continue
        # 4 - don't know how to handle this
        print "Can't use the %s info to send notification" % entry
    emails = set(emails)
    emails_bcc = set(emails_bcc)
    return [x for x in emails if x not in emails_bcc], list(emails_bcc)

def sendMail(object, event):
    """A Zope3 event for sending emails"""
    ploneboard_notify_properties = getToolByName(object,'portal_properties')['ploneboard_notify_properties']
    debug_mode = ploneboard_notify_properties.debug_mode
    notify_encode = ploneboard_notify_properties.notify_encode
    portal = getToolByName(object,"portal_url").getPortalObject()
    portal_transforms = getToolByName(object, "portal_transforms")

    send_from = portal.getProperty('email_from_address')
    if send_from and type(send_from)==tuple:
        send_from = send_from[0]
        
    # Conversation or comment?
    conversation = object.getConversation()
    forum = conversation.getForum()

    send_to, send_to_bcc = _getSendToValues(forum)
    if not send_to and not send_to_bcc:
        return
    
    translation_service = getToolByName(object,'translation_service')
    dummy = _(u"New comment added on the forum: ")
    msg_sbj = u"New comment added on the forum: "
    subject = translation_service.utranslate(domain='Products.PloneboardNotify',
                                             msgid=msg_sbj,
                                             default=msg_sbj,
                                             context=object)
    subject+= forum.Title().decode('utf-8')

    dummy = _(u"Argument is: ")
    msg_txt = u"Argument is: "
    text = translation_service.utranslate(domain='Products.PloneboardNotify',
                                          msgid=msg_txt,
                                          default=msg_txt,
                                          context=object)
    text+=conversation.Title().decode('utf-8')+"\n"

    dummy = _(u"The new message is:")
    msg_txt = u"The new message is:"
    text += translation_service.utranslate(domain='Products.PloneboardNotify',
                                          msgid=msg_txt,
                                          default=msg_txt,
                                          context=object)
    
    try:
        data_body_to_plaintext = portal_transforms.convert("html_to_web_intelligent_plain_text", object.REQUEST.form['text'])
    except:
        # Probably Plone 2.5.x
        data_body_to_plaintext = portal_transforms.convert("html_to_text", object.REQUEST.form['text'])
    body_to_plaintext = data_body_to_plaintext.getData()
    
    text += "\n" + body_to_plaintext.decode('utf-8')
    text += "\n" + object.absolute_url()
    
    mail_host = getToolByName(object, 'MailHost')

    if notify_encode:
        text = text.encode(notify_encode)
    try:
        if debug_mode:
            object.plone_log("Notification from message subject: %s" % subject)
            object.plone_log("Notification from message text:\n%s" % text)
            object.plone_log("Notification from message sent to %s (and to %s in bcc)" % (", ".join(send_to) or 'no-one',
                                                                                          ", ".join(send_to_bcc) or 'no-one'))
        else:
            mail_host.secureSend(text, mto=send_to, mfrom=send_from,
                                 subject=subject, charset=notify_encode, mbcc=send_to_bcc)
    except Exception, inst:
        putils = getToolByName(object,'plone_utils')
        putils.addPortalMessage(_(u'Not able to send notifications'))
        object.plone_log("Error sending notification: %s" % str(inst))

