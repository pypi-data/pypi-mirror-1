from persistent.dict import PersistentDict
from zope import component
from zope import event
from zope import interface
try:
    from zope.app.annotation import interfaces as annointerfaces
except ImportError, err:
    # Zope 2.10 support
    from zope.annotation import interfaces as annointerfaces
from zope.app.event import objectevent
from p4a.audio import interfaces
from p4a.fileimage import DictProperty

class AudioAnnotationAddedEvent(objectevent.ObjectEvent):
    """Annotations added to an object for audio metadata.
    """

class AnnotationAudio(object):
    """An IAudio adapter designed to handle ATCT based file content.
    """

    interface.implements(interfaces.IAudio)

    ANNO_KEY = 'p4a.audio.audioanno.AnnotationAudio'

    def __init__(self, context):
        self.context = context
        annotations = annointerfaces.IAnnotations(context)
        self.audio_data = annotations.get(self.ANNO_KEY, None)
        if self.audio_data is None:
            self.audio_data = PersistentDict()
            annotations[self.ANNO_KEY] = self.audio_data
            event.notify(AudioAnnotationAddedEvent(self))

    title = DictProperty(interfaces.IAudio['title'], 'audio_data')
    description = DictProperty(interfaces.IAudio['description'], 'audio_data')
    rich_description = DictProperty(interfaces.IAudio['rich_description'],
                                    'audio_data')
    artist = DictProperty(interfaces.IAudio['artist'], 'audio_data')
    album = DictProperty(interfaces.IAudio['album'], 'audio_data')
    year = DictProperty(interfaces.IAudio['year'], 'audio_data')
    genre = DictProperty(interfaces.IAudio['genre'], 'audio_data')
    comment = DictProperty(interfaces.IAudio['comment'], 'audio_data')
    idtrack = DictProperty(interfaces.IAudio['idtrack'], 'audio_data')

    variable_bit_rate = DictProperty(interfaces.IAudio['variable_bit_rate'],
                                     'audio_data')
    bit_rate = DictProperty(interfaces.IAudio['bit_rate'], 'audio_data')
    frequency = DictProperty(interfaces.IAudio['frequency'], 'audio_data')
    length = DictProperty(interfaces.IAudio['length'], 'audio_data')
    file = DictProperty(interfaces.IAudio['file'], 'audio_data')
    audio_image = DictProperty(interfaces.IAudio['audio_image'], 'audio_data')

    audio_type = DictProperty(interfaces.IAudio['audio_type'], 'audio_data')

class AnnotationAudioContainer(object):
    """An IAudioContainer adapter designed to handle ATCT based file content.
    """

    interface.implements(interfaces.IAudioContainer)

    ANNO_KEY = 'p4a.audio.audioanno.AnnotationAudioContainer'

    def __init__(self, context):
        self.context = context
        annotations = annointerfaces.IAnnotations(context)
        self.audio_data = annotations.get(self.ANNO_KEY, None)
        if self.audio_data is None:
            self.audio_data = PersistentDict()
            annotations[self.ANNO_KEY] = self.audio_data
            event.notify(AudioAnnotationAddedEvent(self))

    def set_title(self,v):
        self.context.setTitle(v)
    def get_title(self):
        return self.context.Title()
    title = property(get_title, set_title)
    
    def set_description(self,v):
        self.context.setDescription(v)
    def get_description(self):
        return self.context.Description()
    description = property(get_description, set_description)    
    
    artist = DictProperty(interfaces.IAudioContainer['artist'], 'audio_data')
    year = DictProperty(interfaces.IAudioContainer['year'], 'audio_data')
    genre = DictProperty(interfaces.IAudioContainer['genre'], 'audio_data')
    audio_image = DictProperty(interfaces.IAudioContainer['audio_image'], 'audio_data')
