import os
from OFS import Image as ofsimage

from zope import component
from zope import interface
from zope.app.event import objectevent

from p4a.common.descriptors import atfield

from p4a.video import videoanno
from p4a.video import interfaces
from p4a.video import utils
from p4a.plonevideoembed import interfaces as embedifaces

from p4a.fileimage import file as p4afile
from p4a.fileimage import utils as fileutils

from Products.ATContentTypes import interface as atctifaces
from Products.CMFCore import utils as cmfutils

import logging
logger = logging.getLogger('p4a.plonevideo.atct')

class ATCTFolderVideoProvider(object):
    interface.implements(interfaces.IVideoProvider)
    component.adapts(atctifaces.IATFolder)

    def __init__(self, context):
        self.context = context

    @property
    def video_items(self):
        videos = []
        for x in self.context.getFolderContents(full_objects=True):
            video = component.queryAdapter(x, interfaces.IVideo)
            if video is not None:
                videos.append(video)

        return videos

class ATCTTopicVideoProvider(object):
    interface.implements(interfaces.IVideoProvider)
    component.adapts(atctifaces.IATTopic)

    def __init__(self, context):
        self.context = context

    @property
    def video_items(self):
        files = []
        for x in self.context.queryCatalog(full_objects=True):
            adapted = component.queryAdapter(x, interfaces.IVideo)
            if adapted is not None:
                files.append(adapted)

        return files

class AbstractATCTVideo(videoanno.AnnotationVideo):
    """
    """

    interface.implements(interfaces.IVideo)
    component.adapts(atctifaces.IATFile)

    file = None

    title = atfield('title', 'context')
    description = atfield('description', 'context')

    def _get_video_image(self):
        v = self.video_data.get('video_image', None)
        if v == None or v.get_size() == 0:
            return None
        return v
    def _set_video_image(self, v):
        if v == interfaces.IVideo['video_image'].missing_value:
            return
        upload = v
        if isinstance(upload, ofsimage.Image):
            image = upload
        else:
            image = ofsimage.Image(id=upload.filename,
                                   title=upload.filename,
                                   file=upload)
        self.video_data['video_image'] = image
    video_image = property(_get_video_image, _set_video_image)

    @property
    def video_type(self):
        mime_type = self.context.get_content_type()
        adapters = component.getAdapters((self.context,),
                                         interfaces.IVideoDataAccessor)
        if unicode(mime_type) in [adapter[0] for adapter in adapters]:
            accessor = component.getAdapter(self.context,
                                            interfaces.IVideoDataAccessor,
                                            unicode(mime_type))
            return accessor.video_type
        else:
            return None

    def _load_video_metadata(self):
        """Retrieve video metadata from the raw file data and update
        this object's appropriate metadata fields.
        """
        # currently unused

    def _save_video_metadata(self):
        """Write the video metadata fields of this object as metadata
        on the raw file data.
        """
        # currently unused

    def __str__(self):
        return '<p4a.video %s title=%s>' % (self.__class__.__name__, self.title)
    __repr__ = __str__

@interface.implementer(interfaces.IVideo)
@component.adapter(atctifaces.IATLink)
def ATCTLinkVideo(context):
    if not embedifaces.IVideoLinkEnhanced.providedBy(context):
        return None
    return _ATCTLinkVideo(context)

class _ATCTLinkVideo(AbstractATCTVideo):
    """An IVideo adapter designed to handle ATCT based link content.
    """

    ANNO_KEY = 'p4a.plonevideo.atct.ATCTLinkVideo'

@interface.implementer(interfaces.IVideo)
@component.adapter(atctifaces.IATFile)
def ATCTFileVideo(context):
    if not interfaces.IVideoEnhanced.providedBy(context):
        return None
    return _ATCTFileVideo(context)

class _ATCTFileVideo(AbstractATCTVideo):
    """An IVideo adapter designed to handle ATCT based file content.
    """

    ANNO_KEY = 'p4a.plonevideo.atct.ATCTFileVideo'

    def _get_file(self):
        field = self.context.getPrimaryField()
        return field.getEditAccessor(self.context)()
    def _set_file(self, v):
        if v != interfaces.IVideo['file'].missing_value:
            field = self.context.getPrimaryField()
            field.getMutator(self.context)(v)
    file = property(_get_file, _set_file)

    def _load_video_metadata(self):
        """Retrieve video metadata from the raw file data and update
        this object's appropriate metadata fields.
        """
        mime_type = self.context.get_content_type()
        accessor = component.queryAdapter(self.context,
                                          interfaces.IVideoDataAccessor,
                                          unicode(mime_type))
        if accessor is not None:
            field = self.context.getPrimaryField()
            filename = fileutils.write_ofsfile_to_tempfile(
                field.getEditAccessor(self.context)(),
                self.context.getId())
            accessor.load(filename)
            try:
                os.remove(filename)
            except OSError, err:
                logger.exception('Error while trying to clean up temp files')

def load_metadata(obj, evt):
    """An event handler for loading metadata.
    """

    obj._load_video_metadata()

def sync_video_metadata(obj, evt):
    """An event handler for saving id3 tag information back onto the file.
    """

    video = interfaces.IVideo(obj, None)
    if video is not None:
        for description in evt.descriptions:
            if isinstance(description, objectevent.Attributes):
                attrs = description.attributes
                orig = {}
                for key in attrs:
                    if key != 'file' and hasattr(video, key):
                        orig[key] = getattr(video, key)
                if 'file' in attrs:
                    video._load_video_metadata()
                    for key, value in orig.items():
                        setattr(video, key, value)
        video._save_video_metadata()

def attempt_media_activation(obj, evt):
    """Try to activiate the media capabilities of the given object.
    """

    activator = interfaces.IMediaActivator(obj)

    if activator.media_activated:
        return

    mime_type = obj.get_content_type()
    try:
        accessor = component.getAdapter(obj,
                                        interfaces.IVideoDataAccessor,
                                        unicode(mime_type))
    except Exception, e:
        accessor = None

    if accessor is not None:
        activator.media_activated = True
        update_dublincore(obj, evt)
        update_catalog(obj, evt)


def update_dublincore(obj, evt):
    """Update the dublincore properties.
    """

    video = interfaces.IVideo(obj, None)
    if video is not None:
        obj.setTitle(video.title)

def update_catalog(obj, evt):
    """Reindex the object in the catalog.
    """
    obj.reindexObject()

def subtype_changed(evt):
    """Reindex the object in the catalog.
    """
    evt.object.reindexObject()
