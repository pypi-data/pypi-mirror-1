import mimetypes
import os
try:
    from zope.app.annotation import interfaces as annointerfaces
except ImportError, err:
    # Zope 2.10 support
    from zope.annotation import interfaces as annointerfaces
from zope import interface
from OFS import Image as ofsimage
from p4a.audio import interfaces
from p4a.audio.mp3.thirdparty import eyeD3
from p4a.audio.mp3.thirdparty.eyeD3 import frames
from p4a.fileimage import utils as fileutils
import logging

logger = logging.getLogger('p4a.audio.mp3')

def update_audio_image(id3tags, audio_image):
    """Update the id3 tag information with a frame that points to a temporary
    file containing the image data from audio_image.

    """

    mime_type = audio_image.content_type
    desc = u''

    tempfilename = fileutils.write_to_tempfile(audio_image)
    frame = frames.ImageFrame.create(frames.ImageFrame.FRONT_COVER,
                                     tempfilename,
                                     desc)

    imgs = id3tags.getImages()
    if len(imgs) == 0:
        id3tags.frames.append(frame)
    else:
        # find the frame index of the first image so we can
        # replace it with our new image frame
        for i in id3tags.frames:
            if i == imgs[0]:
                index = id3tags.frames.index(i)
                id3tags.frames[index] = frame
                break

    return tempfilename

AUDIO_TYPE = u'MPEG-1 Audio Layer 3'

class MP3AudioDataAccessor(object):
    interface.implements(interfaces.IAudioDataAccessor)

    def __init__(self, context):
        self._filecontent = context

    @property
    def audio_type(self):
        # setup as a read-only property on purpose
        return AUDIO_TYPE

    @property
    def _audio(self):
        audio = getattr(self, '_cached_audio', None)
        if audio is not None:
            return audio
        self._cached_audio = interfaces.IAudio(self._filecontent)
        return self._cached_audio

    @property
    def _audio_data(self):
        annotations = annointerfaces.IAnnotations(self._filecontent)
        return annotations.get(self._audio.ANNO_KEY, None)

    def load(self, filename):
        data = self._audio_data
        id3tags = eyeD3.Tag()
        try:
            id3tags.link(filename)
        except:
            logger.exception('Could not load id3 information using eyeD3 '
                             'from %s' % filename)

            data['title'] = 'ERROR'
            data['artist'] = 'ERROR'
            data['album'] = 'ERROR'
            data['year'] = 1969
            data['idtrack'] = 'ERROR'

            return

        data['title'] = id3tags.getTitle()
        data['artist'] = id3tags.getArtist()
        data['album'] = id3tags.getAlbum()
        data['year'] = id3tags.getYear()
        data['idtrack'] = str(id3tags.getTrackNum()[0])

        image_frames = id3tags.getImages()
        image_frame = None
        if len(image_frames)>0:
            image_frame = image_frames[0]
        if image_frame is not None and image_frame.imageData:
            mime_type = image_frame.mimeType
            ext = mimetypes.guess_extension(mime_type) or '.jpg'
            kwargs = dict(id=os.path.basename(filename)+ext,
                          title='',
                          file=image_frame.imageData)
            if image_frame.mimeType:
                kwargs['content_type'] = image_frame.mimeType
            image = ofsimage.Image(**kwargs)
            data['audio_image'] = image

        try:
            genre = id3tags.getGenre()
        except eyeD3.GenreException:
            if data['title']:
                logger.warn('Invalid genre tag in ' + data['title'])
            else:
                logger.warn('Invalid genre tag')
            genre = None
        if genre and genre.getId() is not None:
            data['genre'] = int(genre.getId())

        data['comment'] = id3tags.getComment()

        mp3_header = eyeD3.Mp3AudioFile(filename)
        variable, bit_rate = mp3_header.getBitRate()
        bit_rate = bit_rate * 1000  # id3 bit_rate info is in Kbps
        data['variable_bit_rate'] = bool(variable)
        data['bit_rate'] = bit_rate
        data['frequency'] = mp3_header.getSampleFreq()
        data['length'] = mp3_header.getPlayTime()

    def store(self, filename):
        id3tags = eyeD3.Tag()
        id3tags.link(filename)
        id3tags.setVersion(eyeD3.ID3_V2_4)
        id3tags.setTextEncoding(eyeD3.frames.UTF_8_ENCODING)

        id3tags.setTitle(self._audio.title or u'')
        id3tags.setArtist(self._audio.artist or u'')
        id3tags.setAlbum(self._audio.album or u'')
        id3tags.setDate(self._audio.year or 0)
        id3tags.setGenre(self._audio.genre)

        for c in id3tags.frames['COMM']:
            id3tags.frames.remove(c)
        if self._audio.comment:
            id3tags.addComment(self._audio.comment)

        # saving the image(s)
        tempfilename = None
        if self._audio.audio_image is not None:
            tempfilename = update_audio_image(id3tags, self._audio.audio_image)

        id3tags.update(version=eyeD3.ID3_V2_4)

        if tempfilename:
            # cleanup temp file
            os.remove(tempfilename)
