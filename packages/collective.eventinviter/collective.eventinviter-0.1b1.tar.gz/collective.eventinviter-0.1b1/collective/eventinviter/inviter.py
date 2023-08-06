from zope.interface import implements
from zope.component import adapts
from interfaces import IInvitationAware, IInviter, IAttendeeEnumerator
from Products.CMFCore.utils import getToolByName
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.Header import Header
from email.Encoders import encode_base64
from Products.MailHost.MailHost import MailHostError

from collective.eventinviter import log
#from collective.eventinviter import EventInviterFactory as _

from StringIO import StringIO

from Products.ATContentTypes.lib.calendarsupport import ICS_HEADER, ICS_FOOTER, PRODID


def create_ics(ical):
    out = StringIO()
    out.write(ICS_HEADER % { 'prodid' : PRODID, })
    out.write(ical)
    out.write(ICS_FOOTER)
    return out.getvalue().replace('\n', '\r\n')


class Inviter(object):
    implements(IInviter)
    adapts(IInvitationAware)

    def __init__(self, context):
        self.context = context

    def invite(self, debug=False):
        enumerator = IAttendeeEnumerator(self.context)
        attendees = enumerator.attendees()
        
        if not attendees:
            #log('No attendees to invite')
            # no attendees to invite
            return
        
        mail_host = self.context.MailHost
        
        portal_url = getToolByName(self.context, 'portal_url')
        portal = portal_url.getPortalObject()
        portal_email_address = portal.getProperty('email_from_address')
        portal_from_name = portal.getProperty('email_from_name')


        ms_tool = getToolByName(self.context, 'portal_membership')
        member = ms_tool.getAuthenticatedMember()
        if member:
            sender_fullname = member.getProperty('fullname') or portal_from_name
            sender_from_address = member.getProperty('email') or portal_email_address
        else:
            sender_fullname = portal_from_name
            sender_from_address = portal_email_address
        
        from_address = '%s <%s>' % (sender_fullname, sender_from_address)

        tr_tool = getToolByName(self.context, 'translation_service')
        def translate(message):
            return tr_tool.utranslate('collective.eventinviter', message, {},
                context=self.context, target_language=None, default=message)

        _ = translate

        subject = _(u'Invite: ') + self.context.Title().decode('utf-8')
        message = _(u'Event invitation from') + ' %s' % (sender_fullname.decode('utf-8'),)
        
        charset = 'iso-8859-1'
        subject = subject.encode(charset)
        msg = MIMEMultipart()
        inner = MIMEText(message, _charset=charset)
        msg.attach(inner)
        
        msg.add_header('Subject', str(Header(subject, charset)))
        msg.add_header('From', from_address)
        
        attachment = create_ics(self.context.getICal())
        p = MIMEBase('text', 'calendar')
        p.set_payload(attachment)
        encode_base64(p)
        p.add_header('Content-Disposition', 'attachment; filename="%s.ics"' % (self.context.getId(),))
        msg.attach(p)

        plone_utils = getToolByName(self.context, 'plone_utils')
        info_message = ''
        debug_results = []
        try:
            for recipient in attendees:
                #log('Inviting attendee: ' + recipient)
                if msg.has_key('To'):
                    msg.replace_header('To', recipient)
                else:
                    msg.add_header('To', recipient)

                debug = mail_host._send(sender_from_address, recipient, msg.as_string(), debug=debug)
            
                # append to message
                info_message = info_message + recipient + ', '
            
                debug_results.append(debug)

            if info_message:
                message = _(u'Sent email invitation to ') + info_message[:-2] + '.'
                plone_utils.addPortalMessage(message, type='info')

        except MailHostError:
            message = _('There\'s a problem with the mail host setup. No email invitations where sent.')
            plone_utils.addPortalMessage(message, type='warning')

        return debug_results

def invite_on_edition(obj, event):
    """ Invite event attendees on event edition.
    """
    inviter = Inviter(obj)
    inviter.invite()


def invite_on_creation(obj, event):
    """ Invite event attendees on event edition.
    """
    inviter = Inviter(obj)
    inviter.invite()

