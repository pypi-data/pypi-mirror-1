import Acquisition
import logging
from zope.formlib import form
from Products.Five.formlib import formbase
from Products.PloneFlashUpload import interfaces
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# XXX The next line throws a DeprecationWarning: Traversable is deprecated.
# __bobo_traverse__ and ITraverser/ITraversable for controlling URL
# traversal have become obsolete. Use an IPublishTraverse adapter
# instead.  This reference will go away in Zope 2.12.
from Products.Five.traversable import Traversable
from Products.PloneFlashUpload import ticket as ticketmod
from Products.PloneFlashUpload import utils
from Products.CMFCore import utils as cmfutils
from zope import event
from z3c.widget.flashupload import upload
from z3c.widget.flashupload.interfaces import FlashUploadedEvent
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.security.interfaces import Unauthorized
from AccessControl import SecurityManagement
from zope.filerepresentation.interfaces import IFileFactory

logger = logging.getLogger('PloneFlashUpload')
logger.level = logging.getLogger().level


class UploadForm(BrowserView, Traversable, upload.UploadForm):
    """displays the swf for uploading files
    """

    template = ViewPageTemplateFile('uploadform.pt')

    def upload_action(self):
        """Location for uploading.
        """

        settings = interfaces.IFlashUploadSettings(self.context)
        return settings.completion_url

    def __call__(self):
        return self.template(template_id='flashupload')


class FlashUploadVars(BrowserView, upload.FlashUploadVars):
    """simple view for the flashupload.pt
    to configure the flash upload swf"""

    allowedFileTypes = () # empty means everything


class UploadFile(BrowserView, Traversable, upload.UploadFile):
    """handles file upload for the flash client.
    flash client sends the data via post as u'Filedata'
    the filename gets sent as: u'Filename'
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        ticket = self.request.form.get('ticket',None)
        if ticket is None:
            # we cannot set post headers in flash, so get the
            # querystring manually
            qs = self.request.get('QUERY_STRING','ticket=')
            ticket = qs.split('=')[-1] or None

        logger.debug('Ticket being used is "%s"' % str(ticket))

        if ticket is None:
            raise Unauthorized('No ticket specified')

        context = utils.non_view_context(self.context)
        url = absoluteURL(context, self.request)
        username = ticketmod.ticketOwner(url, ticket)
        if username is None:
            logger.warn('Ticket "%s" was invalidated, cannot be used '
                        'any more.' % str(ticket))
            raise Unauthorized('Ticket is not valid')

        old_sm = SecurityManagement.getSecurityManager()
        user = utils.find_user(context, username)
        SecurityManagement.newSecurityManager(self.request, user)
        logger.debug('Switched to user "%s"' % username)

        ticketmod.invalidateTicket(url,ticket)
        if self.request.form.get('Filedata', None) is None:
            # flash sends a emtpy form in a pre request in flash version 8.0
            return ""
        fileUpload = self.request.form['Filedata']
        fileName = self.request.form['Filename']
        contentType = self.request.form.get('Content-Type',None)
        factory = IFileFactory(self.context)
        f = factory(fileName, contentType, fileUpload)

        event.notify(FlashUploadedEvent(f))
        result = "filename=%s" %f.getId()

        SecurityManagement.setSecurityManager(old_sm)

        return result


class Configlet(formbase.EditForm):
    """A view for configuring flash upload settings.
    """

    label = u'Plone Flash Upload Configuration'
    form_name = u'Settings'

    template = ViewPageTemplateFile('configlet.pt')
    form_fields = form.FormFields(interfaces.IFlashUploadSettings)


class DisplayUploadView(BrowserView):
    """Returns True or False depending on whether the upload tab is allowed
    to be displayed on the current context.
    """

    def allowed_types(self):
        return [x.getId() for x in self.context.getAllowedTypes()]

    def can_upload(self):
        context = Acquisition.aq_inner(self.context)

        if not context.displayContentsTab():
            return False

        pu = cmfutils.getToolByName(context, 'portal_url')
        portal = pu.getPortalObject()
        settings = interfaces.IFlashUploadSettings(portal)

        # make sure the currently allowed addable types to the folderish
        # context contains at least one of the items defined in
        # IFlashUploadSettings.valid_types

        allowed = set(self.allowed_types())
        valid_types = settings.valid_types.split('\n')
        can_upload = set(valid_types)
        if len(allowed.intersection(can_upload)) == 0:
            return False

        obj = context
        if context.restrictedTraverse('@@plone').isDefaultPageInFolder():
            obj = Acquisition.aq_parent(Acquisition.aq_inner(obj))

        return interfaces.IUploadingCapable.providedBy(obj)

    def upload_url(self):
        context = Acquisition.aq_inner(self.context)
        if context.restrictedTraverse('@@plone').isStructuralFolder():
            url = context.absolute_url()
        else:
            url = Acquisition.aq_parent(context).absolute_url()
        return url + '/flashupload'
