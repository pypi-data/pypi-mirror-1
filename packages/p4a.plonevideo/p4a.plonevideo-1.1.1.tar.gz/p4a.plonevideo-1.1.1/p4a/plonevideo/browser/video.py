import tempfile
import urllib
import urllib2
import Acquisition
from OFS import Image
from zope import component
from zope import event
from zope.app.event import objectevent
from p4a.video import interfaces
from p4a.videoembed import interfaces as embedifaces
from p4a.plonevideoembed import interfaces as pembedifaces
from p4a.video.browser.video import has_contenttagging_support

from Products.CMFCore import utils as cmfutils

def build_ofsimage(url):
    datafile = tempfile.TemporaryFile('w+b')
    fin = urllib2.urlopen(url)
    data = fin.read(64)
    while data:
        datafile.write(data)
        data = fin.read(64)
    fin.close()
    datafile.flush()
    datafile.seek(0)

    ofsimage = Image.Image(id='thumbnail', title='thumbnail', file=datafile)
    datafile.close()

    return ofsimage

class RedirectMixin(object):

    view_name = 'view'

    def redirect(self, url, relative=True):
        response = self.request.response
        if relative:
            response.redirect(self.context.absolute_url() + url)
        else:
            response.redirect(url)
        return ''

    def redirectview(self, msg):
        relative = '/%s?portal_status_message=%s' % (self.view_name,
                                                     urllib.quote(msg))
        return self.redirect(relative)

class QueryException(Exception): pass

class QueryMetadata(RedirectMixin):
    """Query the remote source for video metadata."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def username(self):
        membership = cmfutils.getToolByName(Acquisition.aq_inner(self.context),
                                            'portal_membership')
        return membership.getAuthenticatedMember().getMemberId()

    def query(self):
        context = Acquisition.aq_inner(self.context)

        retriever = component.queryUtility(embedifaces.IVideoMetadataRetriever)
        if retriever is None:
            raise QueryException('Remote metadata retrieval misconfigured.')
        url = embedifaces.ILinkProvider(context).getLink()
        data = retriever.get_metadata(url)

        result = False

        if data is None:
            raise QueryException('Retriever returned no data, most likely '
                                 'cause is that there is no registered '
                                 'lookup component for "%s"' % url)

        video = interfaces.IVideo(context)
        if getattr(data, 'thumbnail_url', None):
            video.video_image = build_ofsimage(data.thumbnail_url)
        if getattr(data, 'title', None):
            video.title = data.title
        if getattr(data, 'description', None):
            video.description = data.description
        if getattr(data, 'author', None):
            video.video_author = data.author
        if getattr(data, 'duration', None):
            video.duration = data.duration

        if getattr(data, 'tags', None) and \
               has_contenttagging_support(context):
            from lovely.tag import interfaces as tagifaces
            tagging = tagifaces.ITagging(context)
            user = self.username()
            tags = set(tagging.getTags([user]))
            for x in data.tags:
                tags.add(x)
            tagging.update(user, tags)

        event.notify(objectevent.ObjectModifiedEvent(context))

    def __call__(self):
        msg = 'Video updated.'
        try:
            self.query()
        except QueryException, e:
            msg = str(e)

        return self.redirectview(msg)

class MultipleQueryMetadata(RedirectMixin):
    """Query the remote source for video metadata."""

    view_name = 'folder_contents'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def query(self):
        successful = 0
        paths = self.request.form.get('paths', [])
        app = self.context.getPhysicalRoot()
        for path in paths:
            obj = app.restrictedTraverse(path)
            if pembedifaces.IVideoLinkEnhanced.providedBy(obj):
                queryview = QueryMetadata(obj, self.request)
                try:
                    queryview.query()
                    successful += 1
                except QueryException, err:
                    pass

        return (len(paths), successful)

    def __call__(self, *args, **kwargs):
        checked, successful = self.query()
        msg = 'While checking %i files, %i video links ' \
              'were updated.' % (checked, successful)
        return self.redirectview(msg)
