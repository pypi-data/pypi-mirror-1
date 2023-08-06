from zope.component import adapts, getMultiAdapter
from zope.interface import implements, Interface
from zope.i18n import translate

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _p
from Products.CMFPlone.utils import safe_unicode

from interfaces import INotificationSender
from raptus.workflownotification import workflownotificationMessageFactory as _

class WorkflownotificationSender(object):
    adapts(Interface)
    implements(INotificationSender)
    
    def __init__(self, context):
        self.context = context
        
    def send(self, action, message, recipients):
        """ send the notifications
        """
        mailhost = getToolByName(self.context, 'MailHost')
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        mfrom = '%s <%s>' % (portal.getProperty('email_from_name', ''), portal.getProperty('email_from_address', ''))
        subject = translate(_('email_subject', default='New notification from ${site}', mapping={'site': portal.getProperty('title', '')}), context=self.context.request)
        wftool = getToolByName(self.context, 'portal_workflow')
        utils = getToolByName(self.context, 'plone_utils')
        mship = getToolByName(self.context, 'portal_membership')
        wnutils = getMultiAdapter((self.context, self.context.request), name=u'workflownotification')
        workflow = wftool.getWorkflowById(wnutils.getWorkflowFor(self.context))
        tdef = workflow.transitions.get(action, None)
        if not tdef:
            return
        issuer = mship.getMemberInfo()
        if not issuer:
            issuer = {'username': 'Anonymous'}
        replacement = dict(name='',
                           title=self.context.Title(),
                           url=self.context.absolute_url(),
                           old_state=translate(_p(utils.getReviewStateTitleFor(self.context)), context=self.context.request),
                           new_state=translate(_p(wftool.getTitleForStateOnType(tdef.new_state_id, self.context.portal_type)), context=self.context.request),
                           transition=translate(_p(tdef.actbox_name), context=self.context.request),
                           issuer=safe_unicode(issuer.get('fullname', issuer['username'])))
        anon_message = message % replacement
        sent = []
        receivers = []
        for r in recipients:
            replacement.update(dict(name=r.name))
            msg = message % replacement
            if not r.email in sent:
                mailhost.secureSend(msg,
                                    mto=r.email,
                                    mfrom=mfrom,
                                    subject=subject,
                                    charset='utf-8')
                sent.append(r.email)
                receivers.append(r)
        return receivers, anon_message
    