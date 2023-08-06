import os
from Acquisition import Implicit, aq_inner
from urlparse import urlsplit

from zope.component import getMultiAdapter
from zope.interface import implements

from kss.core import kssaction

from plone.app.layout.globals.interfaces import IViewView
from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.plonekssview import PloneKSSView

class NotificationFormView(Implicit, PloneKSSView):
    implements(IPloneKSSView, IViewView)
    
    @kssaction
    def displayWorkflowNotificationForm(self, url):
        ksscore = self.getCommandSet('core')

        (proto, host, path, query, anchor) = urlsplit(url)
        action = query.split("workflow_action=")[-1].split('&')[0]
        context = self.context.restrictedTraverse(os.path.dirname(path))
        self.request.URL = '%s/@@workflownotification_form' % context.absolute_url()
        form = getMultiAdapter((context, self.request), name=u'workflownotification_form')(workflow_action=action, standalone=True)
        selector = ksscore.getCssSelector('#contentActionMenus')
        ksscore.setStyle(selector, 'display', 'none')
        selector = ksscore.getCssSelector('#kss-workflownotification_form, #kss-workflownotification_form-overlay')
        ksscore.deleteNode(selector)
        selector = ksscore.getCssSelector('body')
        ksscore.insertHTMLAsLastChild(selector, '%s<div id="kss-workflownotification_form-overlay"></div>' % form.replace('class="workflownotification_form"', 'class="workflownotification_form" id="kss-workflownotification_form"'))
        self.cancelRedirect()
        
    @kssaction
    def removeWorkflowNotificationForm(self):
        ksscore = self.getCommandSet('core')
        
        selector = ksscore.getCssSelector('#contentActionMenus')
        ksscore.setStyle(selector, 'display', 'block')
        selector = ksscore.getCssSelector('#kss-workflownotification_form, #kss-workflownotification_form-overlay')
        ksscore.deleteNode(selector)
        self.cancelRedirect()
        