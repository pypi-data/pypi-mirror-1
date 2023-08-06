from p4a.videoembed.interfaces import *
from Products.Five.browser import BrowserView
from zope.component import getUtility
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class VideoLink(BrowserView):
    """check if video link from known provider. If not, just fall back to
    default view"""

    index = ViewPageTemplateFile("embed.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.metadata_retriever = getUtility(IVideoMetadataRetriever)
        self.embedcode_converter = getUtility(IEmbedCodeConverterRegistry)

    def metadata(self):
        return self.metadata_retriever.get_metadata(self.context.getRemoteUrl())

    def embedcode(self):
        return self.embedcode_converter.get_code(self.context.getRemoteUrl(), 400)

    def __call__(self, *args, **kwargs):
        if not self.embedcode():
            return self.context.aq_inner.restrictedTraverse('link_redirect_view')()
        else:
            return self.index()
