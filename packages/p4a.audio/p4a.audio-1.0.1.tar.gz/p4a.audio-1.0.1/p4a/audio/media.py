from zope import component
from zope import interface
from p4a.audio import interfaces
from p4a.common import feature

_marker = object()

class MediaActivator(object):
    """An adapter for seeing the activation status or toggling activation.
    """

    interface.implements(interfaces.IMediaActivator)
    component.adapts(interface.Interface)

    def __init__(self, context):
        self.context = context

    _audio_activated = feature.FeatureProperty(interfaces.IPossibleAudio,
                                               interfaces.IAudioEnhanced,
                                               'context')
    _audio_container_activated = \
        feature.FeatureProperty(interfaces.IPossibleAudioContainer,
                                interfaces.IAudioContainerEnhanced,
                                'context')

    def media_activated(self, v=_marker):
        if v is _marker:
            if interfaces.IPossibleAudio.providedBy(self.context):
                return self._audio_activated
            elif interfaces.IPossibleAudioContainer.providedBy(self.context):
                return self._audio_container_activated
            return False

        if interfaces.IPossibleAudio.providedBy(self.context):
            self._audio_activated = v
        elif interfaces.IPossibleAudioContainer.providedBy(self.context):
            self._audio_container_activated = v

    media_activated = property(media_activated, media_activated)
