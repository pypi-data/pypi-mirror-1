from zope import interface
from p4a.audio import interfaces
from p4a.subtyper.interfaces import (IPortalTypedDescriptor,
                                     IPortalTypedFolderishDescriptor)

class AudioDescriptor(object):
    interface.implements(IPortalTypedDescriptor)

    title = u'Audio'
    description = u'Audio-based media content'
    type_interface = interfaces.IAudioEnhanced
    for_portal_type = 'File'

class AbstractAudioContainerDescriptor(object):
    interface.implements(IPortalTypedFolderishDescriptor)

    title = u'Audio Container'
    description = u'Container for holding Audio-based media content'
    type_interface = interfaces.IAudioContainerEnhanced

class FolderAudioContainerDescriptor(AbstractAudioContainerDescriptor):
    for_portal_type = 'Folder'

class BTreeFolderAudioContainerDescriptor(AbstractAudioContainerDescriptor):
    for_portal_type = 'Large Plone Folder'

class TopicAudioContainerDescriptor(AbstractAudioContainerDescriptor):
    for_portal_type = 'Topic'
