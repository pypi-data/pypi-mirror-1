from zope import component
from zope import interface
from p4a.plonevideoembed import interfaces
from p4a.common import feature

_marker = object()

class MediaActivator(object):
    """An adapter for seeing the activation status or toggling activation.
    """

    interface.implements(interfaces.IMediaActivator)
    component.adapts(interface.Interface)

    def __init__(self, context):
        self.context = context

    _video_link_activated = feature.FeatureProperty(
        interfaces.IAnyVideoLinkCapable,
        interfaces.IVideoLinkEnhanced,
        'context')

    def media_activated(self, v=_marker):
        if v is _marker:
            if interfaces.IAnyVideoLinkCapable.providedBy(self.context):
                return self._video_link_activated
            return False

        if interfaces.IAnyVideoLinkCapable.providedBy(self.context):
            self._video_link_activated = v

    media_activated = property(media_activated, media_activated)
