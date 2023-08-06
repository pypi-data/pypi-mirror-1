from zope.interface import Interface

from zope.interface import implements
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName




from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from betahaus.portlet.maillist import MailListPortletMessageFactory as _

class IMailListPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    
    header = schema.TextLine(title=_(u"Portlet header"),
                             description=_(u"Title of the rendered portlet"),
                             required=True)
    
    body = schema.Text(title=_(u"Optional body text under the headline"),
                       required=False)
    
    subscr_email = schema.TextLine(title=_(u"Subscription address"),
                                  description=_(u"Email address to send subscription requests to."),
                                  required=True)
    
    subscr_subject = schema.TextLine(title=_(u"Subscription subject"),
                                     description=_(u"Text to pass along in the subject header, usually 'subscribe'."),
                                     required=False,
                                     default=u"subscribe")
    
    leave_email = schema.TextLine(title=_(u"Leave address, if different then subscription"),
                                  description=_(u"Email address to send leave requests to. Leave empty if it is the same as the subscription address."),
                                  required=False)
    
    leave_subject = schema.TextLine(title=_(u"Leave subject"),
                                    description=_(u"Text to pass along in the subject header, usually 'unsubscribe'."),
                                    required=False,
                                    default=u"unsubscribe")

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IMailListPortlet)

    header = u""
    body = u""
    subscr_email = u""
    subscr_subject = u"subscribe"
    leave_email = u""
    leave_subject = u"unsubscribe"
    
    def __init__(self, header=u"", body=u"", subscr_email=u"", subscr_subject=u"subscribe", leave_email=u"", leave_subject=u"unsubscribe"):
        self.header = header
        self.body = body
        self.subscr_email = subscr_email
        self.subscr_subject = subscr_subject
        self.leave_email = leave_email or subscr_email
        self.leave_subject = leave_subject

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Mail list portlet"

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('maillistportlet.pt')

    def update(self):
        request = self.context.REQUEST
        if not request.get('maillist.submitted'):
            return self.context

        urltool = getToolByName(self.context, "portal_url")
        portal = urltool.getPortalObject()
        email_charset = portal.getProperty('email_charset')
        MailHost = self.context.MailHost
        plone_utils = getToolByName(self.context, 'plone_utils')
        
        email = request.get('email_address', None)
        to_email = portal.getProperty('email_from_address')
        subject = ''
        
        if not email:
            # No emailaddress was entered.
            return self.context
        
        action = request.get('maillist')
        if action == 'subscribe':
            to_email = self.subscribe_email
            subject =  self.data.subscr_subject
        elif action == 'unsubscribe':
            to_email = self.leave_email
            subject = self.data.leave_subject
        else:
            return self.context

        # Send the subscription mail:
        from_address = body = email
        
        try:
            MailHost.send(# body
                          body.encode(email_charset),
                          #to
                          mto = to_email.encode(email_charset),
                          # from 
                          mfrom = email.encode(email_charset),
                          # subject
                          subject = subject.encode(email_charset),
                          )
        except:
            plone_utils.addPortalMessage(_('Sorry, there was a problem %sing to the mailinglist. Please contact site administrator. ' % action))
        else:
            plone_utils.addPortalMessage(_('You have been %sd to the mailinglist.' % action))
        self.context.REQUEST.response.redirect(request.get('maillist.camefrom'))
        
    @property
    def subscribe_email(self):
        return self.data.subscr_email
    
    @property
    def leave_email(self):
        return self.data.leave_email or self.data.subscr_email
    
    
    def maillistform(self):
        return '%s' % getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state').portal_url()

# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IMailListPortlet)

    def create(self, data):
        return Assignment(**data)

# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IMailListPortlet)
