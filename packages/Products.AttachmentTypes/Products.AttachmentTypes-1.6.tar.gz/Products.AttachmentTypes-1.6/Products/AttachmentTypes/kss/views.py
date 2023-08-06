from zope.interface import alsoProvides

from kss.core import kssaction
from plone.app.kss.plonekssview import PloneKSSView

from plone.app.layout.globals.interfaces import IViewView

from Products.AttachmentTypes.utils import getAttachments, getImages, getLinks

class DynamicAttachments(PloneKSSView):
    """
    """

    def getAttachmentsHTML(self):
        return self.context.widget_attachments_list(attachments=getAttachments(self.context))

    def getImagesHTML(self):
        return self.context.widget_images_list(images=getImages(self.context))

    def getLinksHTML(self):
        return self.context.widget_links_list(links=getLinks(self.context))

    @kssaction
    def addAttachments(self):
        status, message, new_context = self.context.doAddAttachments(self.request.get('attachmentFiles', []))

        alsoProvides(self, IViewView)

        ksscore = self.getCommandSet('core')
        plone = self.getCommandSet('plone')

        html = self.getAttachmentsHTML()

        plone.issuePortalMessage(message)
        ksscore.replaceHTML(ksscore.getHtmlIdSelector('attachments_list'), html)
        ksscore.setAttribute(ksscore.getCssSelector('#attachment-controls .collapsibleContent .collapsible'), 'style', '')

    @kssaction
    def addImages(self):
        status, message, new_context = self.context.doAddImages(self.request.get('imageFiles', []))

        alsoProvides(self, IViewView)

        ksscore = self.getCommandSet('core')
        plone = self.getCommandSet('plone')

        html = self.getImagesHTML()

        plone.issuePortalMessage(message)
        ksscore.replaceHTML(ksscore.getHtmlIdSelector('images_list'), html)
        ksscore.setAttribute(ksscore.getCssSelector('#image-controls .collapsibleContent .collapsible'), 'style', '')

    @kssaction
    def addLinks(self):
        status, message, new_context = self.context.doAddLinks(self.request.get('links', []))

        alsoProvides(self, IViewView)

        ksscore = self.getCommandSet('core')
        plone = self.getCommandSet('plone')

        html = self.getLinksHTML()

        plone.issuePortalMessage(message)
        ksscore.replaceHTML(ksscore.getHtmlIdSelector('links_list'), html)
        ksscore.setAttribute(ksscore.getCssSelector('#link-controls .collapsibleContent .collapsible'), 'style', '')

    @kssaction
    def deleteAttachments(self, container):
        status, message = self.context.doDeleteAttachments(self.request.get('attachmentIds', []))

        alsoProvides(self, IViewView)

        ksscore = self.getCommandSet('core')
        plone = self.getCommandSet('plone')

        if container == 'attachments_list':
            html = self.getAttachmentsHTML()
        if container == 'images_list':
            html = self.getImagesHTML()
        if container == 'links_list':
            html = self.getLinksHTML()

        plone.issuePortalMessage(message)
        ksscore.replaceHTML(ksscore.getHtmlIdSelector(container), html)

    @kssaction
    def moveDownAttachments(self, container):
        message = self.context.doMoveDownAttachments(self.request.get('attachmentIds', []))

        alsoProvides(self, IViewView)

        ksscore = self.getCommandSet('core')
        plone = self.getCommandSet('plone')

        if container == 'attachments_list':
            html = self.getAttachmentsHTML()
        if container == 'images_list':
            html = self.getImagesHTML()
        if container == 'links_list':
            html = self.getLinksHTML()

        plone.issuePortalMessage(message)
        ksscore.replaceHTML(ksscore.getHtmlIdSelector(container), html)

    @kssaction
    def moveUpAttachments(self, container):
        message = self.context.doMoveUpAttachments(self.request.get('attachmentIds', []))

        alsoProvides(self, IViewView)

        ksscore = self.getCommandSet('core')
        plone = self.getCommandSet('plone')

        if container == 'attachments_list':
            html = self.getAttachmentsHTML()
        if container == 'images_list':
            html = self.getImagesHTML()
        if container == 'links_list':
            html = self.getLinksHTML()

        plone.issuePortalMessage(message)
        ksscore.replaceHTML(ksscore.getHtmlIdSelector(container), html)

    @kssaction
    def renameAttachments(self, container):
        message = self.context.doRenameAttachments(self.request.get('attachmentTitles', []))

        alsoProvides(self, IViewView)

        ksscore = self.getCommandSet('core')
        plone = self.getCommandSet('plone')

        if container == 'attachments_list':
            html = self.getAttachmentsHTML()
        if container == 'images_list':
            html = self.getImagesHTML()

        plone.issuePortalMessage(message)
        ksscore.replaceHTML(ksscore.getHtmlIdSelector(container), html)

    @kssaction
    def editLinks(self):
        message = self.context.doEditLinks(self.request.get('links', []))

        alsoProvides(self, IViewView)

        ksscore = self.getCommandSet('core')
        plone = self.getCommandSet('plone')

        html = self.getLinksHTML()

        plone.issuePortalMessage(message)
        ksscore.replaceHTML(ksscore.getHtmlIdSelector('links_list'), html)