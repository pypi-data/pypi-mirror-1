import datetime
import urllib
import Acquisition
import AccessControl

from zope import event
from zope import component
from zope import interface
from zope import schema
from zope.formlib import form
from zope.app.event import objectevent
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory

from p4a.audio import genre
from p4a.audio import interfaces
from p4a.audio.browser import media
from p4a.audio.browser import widget
from p4a.fileimage.image._widget import ImageURLWidget
from p4a.common import at
from p4a.common import formatting

from Products.CMFCore import utils as cmfutils
from Products.Five.browser import pagetemplatefile
from Products.Five.formlib import formbase
from Products.statusmessages import interfaces as statusmessages_ifaces

_ = MessageFactory('plone4artists')

def has_contentrating_support(context):
    try:
        import contentratings
    except ImportError, e:
        return False
    return True

def has_contentlicensing_support(context):
    try:
        from Products import ContentLicensing
    except ImportError, e:
        return False

    tool = cmfutils.getToolByName(context, 'portal_contentlicensing', None)
    return tool is not None

def has_contenttagging_support(context):
    try:
        from lovely.tag import interfaces as tagifaces
    except ImportError, e:
        return False
    return component.queryUtility(tagifaces.ITaggingEngine) is not None

class FeatureMixin(object):
    def has_contentrating_support(self):
        return has_contentrating_support(Acquisition.aq_inner(self.context))

    def has_contentlicensing_support(self):
        return has_contentlicensing_support(Acquisition.aq_inner(self.context))

    def has_contenttagging_support(self):
        return has_contenttagging_support(Acquisition.aq_inner(self.context))

class IAudioView(interface.Interface):
    def title(): pass
    def artist(): pass
    def album(): pass
    def year(): pass
    def genre(): pass
    def comment(): pass
    def variable_bit_rate(): pass
    def bit_rate(): pass
    def frequency(): pass
    def length(): pass
    def audio_type(): pass
    def has_media_player(): pass

class IAudioListedSingle(interface.Interface):
    def single(obj=None): pass
    def safe_audio(obj=None, pos=None, relevance=None): pass

class AudioListedSingle(FeatureMixin):
    """Audio listed single."""

    template = pagetemplatefile.ViewPageTemplateFile('audio-listed-single.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.membership = cmfutils.getToolByName(context, 'portal_membership')
        self.portal_url = cmfutils.getToolByName(context, 'portal_url') \
                          .getPortalObject().absolute_url()
        self._player_count = 0
        self.discussion = cmfutils.getToolByName(context,
                                                 'portal_discussion')

    def player_count(self):
        self._player_count += 1
        return self._player_count

    def __call__(self):
        return self.single()

    def _imageurlwidget(self, audio):
        field = interfaces.IAudio['audio_image'].bind(audio)
        w = ImageURLWidget(field, self.request)
        return w()

    def _playerwidget(self, audio_item):
        field = interfaces.IAudio['file'].bind(audio_item)
        w = widget.MediaPlayerWidget(field, self.request)
        return w()

    def portal_url(self):
        return self.portal_url

    def single(self, obj=None, pos=None, relevance=None):
        return self.template(audio=self.safe_audio(obj=obj, pos=pos,
                                                   relevance=relevance))

    def safe_audio(self, obj=None, pos=None, relevance=None):
        if obj is None:
            obj = Acquisition.aq_inner(self.context)
        obj = interfaces.IAudio(obj, None)
        if obj is None:
            return None

        contentobj = obj.context
        fsize = contentobj.getFile().get_size()
        author_username = author = contentobj.Creator()
        author_info = self.membership.getMemberInfo(author_username)
        if author_info is not None:
            author = author_info.get('fullname', author_username)
        creation_time = contentobj.created()
        creation_time = datetime.date(creation_time.year(),
                                      creation_time.month(),
                                      creation_time.day())
        creation_time = formatting.fancy_date_interval(creation_time)
        if self.has_contenttagging_support():
            tagview = component.getMultiAdapter(
                (contentobj, self.request),
                interface=interface.Interface,
                name=u'tag_info')
            tags = ({'name': obj,
                     'url': tagview.tag_url(obj) }
                    for obj in tagview.contextual_tags())
        else:
            tags = []

        avgrating = None
        rating_count = None
        if self.has_contentrating_support():
            ratingview = component.getMultiAdapter(
                (contentobj, self.request),
                interface=interface.Interface,
                name=u'user_rating_view')
            avgrating = int(ratingview.averageRating)
            rating_count = int(ratingview.numberOfRatings)

        if self.discussion.isDiscussionAllowedFor(contentobj):
            commenting_allowed = True
            disc = self.discussion.getDiscussionFor(contentobj)
            commenting_count = disc.replyCount(contentobj)
            commenting_last = None

            for x in disc.objectValues():
                if commenting_last is None or \
                       x.created() > commenting_last.created():
                    commenting_last = x
            if commenting_last is not None:
                created = commenting_last.created()
                created = datetime.date(created.year(),
                                        created.month(),
                                        created.day())
                commenting_last = formatting.fancy_date_interval(created)
                commenting_last = commenting_last.lower()
        else:
            commenting_count = 0
            commenting_last = ''
            commenting_allowed = False

        max_length = 30
        description = ''
        count = 0
        for c in contentobj.Description():
            if c == ' ':
                count += 1
            if count >= max_length:
                break
            description += c

        if len(description) != len(contentobj.Description()):
            description += ' ...'

        has_image = obj.audio_image is not None
        length = obj.length or 0
        audio = {
            'title': obj.title,
            'content_author': author_username,
            'content_author_name': author,
            'creation_time': creation_time,
            'tags': tags,
            'description': description,
            'album': obj.album,
            'artist': obj.artist,
            'mime_type': contentobj.getContentType,
            'year': obj.year,
            'idtrack':obj.idtrack,
            'url': contentobj.absolute_url(),
            'size': formatting.fancy_data_size(fsize),
            'length': formatting.fancy_time_amount(length,
                                                   show_legend=False),
            'icon': contentobj.getIcon(),
            'playerwidget': self._playerwidget(obj),
            'has_image': has_image,
            'imageurlwidget': self._imageurlwidget(obj),
            'avgrating': avgrating,
            'rating_count': rating_count,
            'player_count': self.player_count(),
            'relevance': relevance,
            'commenting_count': commenting_count,
            'commenting_last': commenting_last,
            'commenting_allowed': commenting_allowed,
             }

        if pos is not None:
            audio['oddeven'] = ODDEVEN[pos % 2]

        return audio

class AudioTrackListedSingle(AudioListedSingle):
    """Audio track listed single."""

    template = pagetemplatefile.ViewPageTemplateFile('audio-tracklisting-single.pt')

class AudioView(object):
    """
    """

    def __init__(self, context, request):
        self.audio_info = interfaces.IAudio(context)

        mime_type = unicode(context.get_content_type())
        self.media_player = component.queryAdapter(self.audio_info.file,
                                                   interfaces.IMediaPlayer,
                                                   mime_type)

    def title(self): return self.audio_info.title
    def description(self): return self.audio_info.description
    def artist(self): return self.audio_info.artist
    def album(self): return self.audio_info.album
    def year(self): return self.audio_info.year
    def comment(self): return self.audio_info.comment
    def idtrack(self): return self.audio_info.idtrack
    def variable_bit_rate(self): return self.audio_info.variable_bit_rate
    def audio_type(self): return self.audio_info.audio_type
    def has_media_player(self): return self.media_player is not None
    def rich_description(self): return self.audio_info.rich_description

    def genre(self):
        g = self.audio_info.genre
        if g in genre.GENRE_VOCABULARY:
            return genre.GENRE_VOCABULARY.getTerm(g).title
        return u''

    def frequency(self):
        if not self.audio_info.frequency:
            return 'N/A'
        return '%i Khz' % (self.audio_info.frequency / 1000)

    def bit_rate(self):
        return '%i Kbps' % (self.audio_info.bit_rate / 1000)

    def length(self):
        return formatting.fancy_time_amount(self.audio_info.length)

class AudioPageView(media.BaseMediaDisplayView, FeatureMixin):
    """Page for displaying audio.
    """

    adapted_interface = interfaces.IAudio
    media_field = 'file'

    form_fields = form.FormFields(interfaces.IAudio)
    label = u'View Audio Info'

    @property
    def template(self):
        return self.index

class PopupAudioPageView(media.BaseMediaDisplayView):
    """Page for displaying audio.
    """

    adapted_interface = interfaces.IAudio
    media_field = 'file'

    form_fields = ()
    label = u'Popup Audio Player'

    @property
    def template(self):
        return self.index

def applyChanges(context, form_fields, data, adapters=None):
    if adapters is None:
        adapters = {}

    changed = []

    for form_field in form_fields:
        field = form_field.field
        # Adapt context, if necessary
        interface = field.interface
        adapter = adapters.get(interface)
        if adapter is None:
            if interface is None:
                adapter = context
            else:
                adapter = interface(context)
            adapters[interface] = adapter

        name = form_field.__name__
        newvalue = data.get(name, form_field) # using form_field as marker
        if (newvalue is not form_field) and (field.get(adapter) != newvalue):
            changed.append(name)
            field.set(adapter, newvalue)

    return changed

class SimpleTagging(object):

    def __init__(self, context):
        from p4a.plonetagging.content import UserTagging
        from p4a.plonetagging.utils import escape, unescape
        self.tagging = UserTagging(context)
        self.escape = escape
        self.unescape = unescape

    def _get_tags(self):
        return self.escape(self.tagging.tags)
    def _set_tags(self, v):
        if not v or not v.strip():
            self.tagging.tags = []
        else:
            self.tagging.tags = self.unescape(v)
    tags = property(_get_tags, _set_tags)

class AudioEditForm(formbase.EditForm):
    """Form for editing audio fields.
    """

    template = pagetemplatefile.ViewPageTemplateFile('audio-edit.pt')
    form_fields = form.Fields(interfaces.IAudio)
    form_fields['rich_description'].custom_widget = at.RichTextEditWidget
    label = _(u'Edit Audio Data')

    def display_tags(self):
        username = AccessControl.getSecurityManager().getUser().getId()
        return username == self.context.getOwner().getId() and \
               has_contenttagging_support(self.context)

    def update(self):
        self.adapters = {}
        form_fields = self.form_fields
        if self.display_tags():
            from lovely.tag.interfaces import IUserTagging
            field = schema.TextLine(__name__='tags',
                                    title=u'Tags',
                                    description=u'Enter as many tags as you '
                                                u'like, separated by spaces.  '
                                                u'If you need a tag with '
                                                u'spaces, encase the tag in '
                                                u'double quotes; the double '
                                                u'quotes will be ignored.',
                                    required=False)
            field.interface = IUserTagging
            form_fields = self.form_fields + form.Fields(field)
            names = ['title', 'tags', 'description']
            for field in interfaces.IAudio:
                if field not in names:
                    names.append(field)
            form_fields = form_fields.select(*names)

            simpletagging = SimpleTagging(self.context.context)
            self.adapters[IUserTagging] = simpletagging
        self.form_fields = form_fields

        super(AudioEditForm, self).update()

    def setUpWidgets(self, ignore_request=False):
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, ignore_request=ignore_request
            )

    @form.action(_(u"Apply"), condition=form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        changed = applyChanges(
            self.context, self.form_fields, data, self.adapters)
        if changed:
            attrs = objectevent.Attributes(interfaces.IAudio, *changed)
            event.notify(
                objectevent.ObjectModifiedEvent(self.context, attrs)
                )
            # TODO: Needs locale support. See also Five.form.EditView.
            self.status = _(u"Successfully updated")
        else:
            self.status = _(u'No changes')
        statusmessages_ifaces.IStatusMessage(
            self.request).addStatusMessage(self.status, 'info')
        redirect = self.request.response.redirect
        return redirect(self.context.absolute_url()+'/view')

class AudioEditMacros(formbase.PageForm):
    # short cut to get to macros more easily
    def __getitem__(self, name):
        if hasattr(self.template, 'macros'):
            template = self.template
        elif hasattr(self.template, 'default_template'):
            template = self.template.default_template
        else:
            raise TypeError('Could not lookup macros on the configured '
                            'template')

        if getattr(template.macros, '__get__', None):
            macros = template.macros.__get__(template)
        else:
            macros = template.macros

        if name == 'macros':
            return macros
        return macros[name]

class AudioContainerEditForm(formbase.EditForm):
    """Form for editing audio container fields.
    """

    form_fields = form.FormFields(interfaces.IAudioContainer)
    label = u'Edit Audio Container Data'

    @form.action(_(u"Apply"), condition=form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        changed = applyChanges(
            self.context, self.form_fields, data, self.adapters)
        if changed:
            attrs = objectevent.Attributes(interfaces.IAudioContainer, *changed)
            event.notify(
                objectevent.ObjectModifiedEvent(self.context, attrs)
                )
            # TODO: Needs locale support. See also Five.form.EditView.
            self.status = _(u"Successfully updated")
        else:
            self.status = _(u'No changes')
        redirect = self.request.response.redirect
        msg = urllib.quote(translate(self.status))
        return redirect(self.context.absolute_url()+
                        '/view?portal_status_message=%s' % msg)

class AudioStreamerView(object):
    """View for streaming audio file as M3U.
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self):
        file_sans_ext = self.context.getId()
        pos = file_sans_ext.rfind('.')
        if pos > -1:
            file_sans_ext = file_sans_ext[:pos]
        
        response = self.request.response
        response.setHeader('Content-Type', 'audio/x-mpegurl')
        response.setHeader('Content-Disposition', 
                           'attachment; filename="%s.m3u"' % file_sans_ext)
        return self.request.URL1 + '\n'

ODDEVEN = ['even', 'odd']

class AudioContainerView(formbase.PageDisplayForm, FeatureMixin):
    """View for audio containers.
    """
    adapted_interface = interfaces.IAudioContainer

    @property
    def template(self):
        return self.index

    form_fields = form.FormFields(interfaces.IAudioContainer)
    label = u'View Audio Container Info'

    def __init__(self, context, request):

        self.audio_info = interfaces.IAudioContainer(context)

        self.context = context
        self.request = request
        self._audio_items = None
        self._total_length = 0
        self.provider = interfaces.IAudioProvider(context)

    def sort_audio_items(self, audio_items_to_sort = []):
        if audio_items_to_sort == []:
            return []
        else:
            pivot = audio_items_to_sort[0]              
            greater = self.sort_audio_items([x for x in audio_items_to_sort[1:] if x['idtrack'] < pivot['idtrack']])
            lesser = self.sort_audio_items([x for x in audio_items_to_sort[1:] if x['idtrack'] >= pivot['idtrack']])
            res = lesser + [pivot] + greater
            for pos, item in enumerate(res):
                item['oddeven'] = ODDEVEN[pos % 2]
            return res

    def audio_items(self):
        return self.provider.audio_items

    def total_length(self):
        return formatting.fancy_time_amount(self._total_length)

    def artist(self):
        return self.audio_info.artist

    def year(self):
        return self.audio_info.year

    def genre(self):
        g = self.audio_info.genre
        if g in genre.GENRE_VOCABULARY:
            return genre.GENRE_VOCABULARY.getTerm(g).title
        return u''

    def has_syndication(self):
        try:
            view = self.context.restrictedTraverse('@@rss.xml')
            return True
        except:
            # it's ok if this doesn't exist, just means no syndication
            return False

    def should_display_summary(self):
        return self.audio_info.artist \
               or self.audio_info.year \
               or self.audio_info.genre

    def should_display_art(self):
        return self.audio_info.audio_image is not None
