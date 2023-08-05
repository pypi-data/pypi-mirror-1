from zope import interface
from zope import schema

class ILinkHolder(interface.Interface):
    """A zope schema based interface for getting and setting a url.
    """

    url = schema.TextLine(title=u'Video URL',
                          required=False)

class IVideoLinkSupport(interface.Interface):
    """Provides certain information about video support.
    """

    support_enabled = schema.Bool(title=u'Video Support Enabled?',
                                  required=True,
                                  readonly=True)

class IAnyVideoLinkCapable(interface.Interface):
    """Marker interface declaring that a particular class/object can have
    link information pointing to video.
    """

class IVideoLinkEnhanced(interface.Interface):
    """Marker interface declaring that a particular class/object is
    identified as being a link to video.
    """

class IMediaActivator(interface.Interface):
    """For seeing the activation status or toggling activation."""

    media_activated = schema.Bool(title=u'Media Activated',
                                  required=True,
                                  readonly=False)
