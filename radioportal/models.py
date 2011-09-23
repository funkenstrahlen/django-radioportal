# -*- coding: utf-8 -*-


from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.db.models import Min, Max

from autoslug import AutoSlugField

import hashlib

class Show(models.Model):
    name = models.CharField(max_length=50, unique=True,
        verbose_name=_('Name of the show'),
    )
    slug = AutoSlugField(populate_from='name', always_update=True)
    url = models.URLField(verify_exists=False, blank=True, default='',
        verbose_name=_('Homepage of the Show'))
    twitter = models.CharField(max_length=100, blank=True, default='')
    chat = models.CharField(max_length=100, blank=True, default='')
    description = models.CharField(max_length=200, blank=True, default='',
        verbose_name=_("Description"))
    abstract = models.TextField(blank=True, default='',
        verbose_name=_('Longer description of the show'))

    LICENCES = (
        ('none', _('none')),
        ('cc-by', _('cc-by')),
        ('cc-by-sa', _('cc-by-sa')),
        ('cc-by-nd', _('cc-by-nd')),
        ('cc-by-nc', _('cc-by-nc')),
        ('cc-by-nc-sa', _('cc-by-nc-sa')),
        ('cc-by-nc-nd', _('cc-by-nc-nd')),
    )

    licence  = models.CharField(max_length=100,
        choices=LICENCES, default=LICENCES[0][0])

    defaultShortName = models.SlugField(default='',
        help_text=_('Used to construct the episode' +
                    ' identifier.'),
        verbose_name=_("Abbreviation of the show"))
    nextEpisodeNumber = models.PositiveIntegerField(default=1,
        help_text=_('The number of the next episode to be aired. Used to construct the episode identifier'),
        verbose_name=_("Number of the next episode"))

    icon = models.ImageField(upload_to="show-icons/", blank=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        permissions = (
            ('change_episodes', _('Delete Episodes')),
        )

class ShowFeed(models.Model):
    show = models.OneToOneField(Show)
    enabled = models.BooleanField()
    feed = models.URLField(max_length=240, blank=True,
        verbose_name=_("Feed of the podcast"),)
    titlePattern = models.CharField(max_length=240, blank=True,
        verbose_name=_("Regular expression for the title"),
        help_text=_(u"Used to extract the id and title from the »title« field of the feed. Should contain the match groups »id« and »title«. "))


class Episode(models.Model):
    """
        a single Episode of a show, which should be relayed or was relayed in
        the past
    """
    STATUS = (
        ('ARCHIVED', _("Archived Episode")),
        ('RUNNING', _("Running Episode")),
        ('UPCOMING', _("Upcoming Episode")),
    )
    show = models.ForeignKey(Show, verbose_name=_("Show"))
    slug = models.SlugField(max_length=30, default='',
        verbose_name=_("Short Name"))
    
    def begin(self):
        return self.parts.aggregate(Min('begin'))['begin__min']
    
    def end(self):
        return self.parts.aggregate(Max('end'))['end__max']
    
    def title(self):
        if len(self.parts.all()) > 0:
            return self.parts.all()[0].title
        return None
    
    def description(self):
        if len(self.parts.all()) > 0:
            return self.parts.all()[0].description
        return None        
    
    def url(self):
        if len(self.parts.all()) > 0:
            return self.parts.all()[0].url
        return None        
    
    status = models.CharField(max_length=10,
        choices=STATUS, default=STATUS[2][0])

    current_part = models.ForeignKey('EpisodePart', blank=True, null=True, related_name="current_episode")

    def __unicode__(self):
        if len(self.parts.all()) > 0:
            return self.parts.all()[0].__unicode__()
        else:
            return u'%s' % self.slug

#    def save(self, force_insert=False, force_update=False):
#        #if self.title == '':
#        #    self.title = _("Episode %(number)s of %(show)s") % \
#        #                    {'number': self.slug, 'show': self.show.name}
#        self.slug = self.slug.lower()
#        if self.slug == re.sub("\W", "", self.title):
#            self.title = ""
#        super(Episode, self).save(force_insert, force_update)

    class Meta:
        unique_together = (('show', 'slug'),)


class EpisodePart(models.Model):
    """
    a part of an episode, i.e 'intro' or 'interview with first caller'
    should be used for timelines
    """
    episode = models.ForeignKey(Episode, related_name='parts')
    title = models.CharField(max_length=200, blank=True, default='', verbose_name=_("Topic"))
    description = models.CharField(max_length=200, blank=True,
        default='', verbose_name=_("Description"))    
    begin = models.DateTimeField(verbose_name=_("Begin"))
    end = models.DateTimeField(blank=True, null=True, verbose_name=_("End"))
    url = models.URLField(blank=True, verify_exists=False,
        help_text=_('Page of the Episode'),
        verbose_name=_("URL"))

    def __unicode__(self):
        return u'%s%s%s' % (self.episode.slug, " " if self.title else"", self.title, )

    class Meta:
        ordering = ['-id']

class Graphic(models.Model):
    file = models.ImageField(upload_to='archiv', blank=True)
    episode = models.ForeignKey('EpisodePart', related_name='graphics')

    def __unicode__(self):
        return self.file.name + unicode(": ") + unicode(self.episode)


class Recording(models.Model):
    episode = models.ForeignKey('EpisodePart', related_name='recordings')
    path = models.CharField(max_length=250)

    format = models.CharField(max_length=50)
    bitrate = models.CharField(max_length=50)

    publicURL = models.URLField(verify_exists=False, default='')
    isPublic = models.BooleanField()
    size = models.PositiveIntegerField()
    
    running = models.BooleanField()


class StreamSetup(models.Model):
    # Status
    #running = models.BooleanField(default=False,
    #    help_text=_("A Stream of this setup is running"))
    def running(self):
        return self.stream_set.filter(running=True).count() > 0

    # Meta data from stream
    cluster = models.CharField(max_length=40, unique=True,
        help_text=_("Stream identifier from backend"))
    streamCurrentSong = models.CharField(max_length=255,
        blank=True, default='',
        help_text=_(u"Property »current_song« from stream meta data"))
    streamGenre = models.CharField(max_length=250, blank=True, default='',
        help_text=_(u"Property »genre« from stream meta data"))
    streamShow = models.CharField(max_length=250, blank=True, default='',
        help_text=_(u"Property »show« from stream meta data"))
    streamDescription = models.CharField(max_length=250,
        blank=True, default='',
        help_text=_(u"Property »description« from stream meta data"))
    streamURL = models.URLField(verify_exists=False, blank=True, default='',
        help_text=_(u"Property »url« from stream meta data"))

    show = models.ManyToManyField(Show, blank=True, null=True,
        help_text=_('show which is assigned to this setup'),
        verbose_name=_('Associated shows'))
    currentEpisode = models.OneToOneField(Episode, blank=True, null=True)

    graphic_differ_by = models.CharField(max_length=255, blank=True)

    graphic_title = models.CharField(max_length=255, blank=True)

    def running_streams(self):
        return self.stream_set.filter(running=True)

    def updateRunning(self):
        self.running = False
        for stream in self.stream_set.all():
            if stream.running:
                self.running = True
                break
        self.save()

    def __unicode__(self):
        return _("Setup for %(cluster)s" % {'cluster': self.cluster})


class Stream(models.Model):
    """
        a single stream for a episode of a show, which is relayed by different
        Relays
    """

    setup = models.ForeignKey(StreamSetup)

    mount = models.CharField(max_length=80, unique=True)
    running = models.BooleanField(default=False)

    FORMATS = (
        ('mp3', _('MP3')),
        ('aac', _('AAC')),
        ('ogg', _('Ogg/Vorbis')),
        ('ogm', _('Ogg/Theora')),
    )

    format = models.CharField(max_length=100,
        choices=FORMATS, default=FORMATS[0][0])
    bitrate = models.CharField(max_length=100, default='0')

    ENCODINGS = (
        ('UTF-8', _('UTF-8')),
        ('ISO8859-15', _('ISO8859-15')),
    )

    encoding = models.CharField(max_length=255,
        choices=ENCODINGS, default=ENCODINGS[0][0])

    def updateRunning(self):
        self.running = False
        self.save()
        if self.setup_id:
            self.setup.updateRunning()

    def __unicode__(self):
        return unicode("%s at %s at %s" % \
                            (self.format, self.bitrate, self.mount))

    WAVE = (
        ('sine', _("Sine")),
        ('square', _("Square")),
        ('saw', _("Saw")),
        ('triangle', _("Triangle")),
        ('silence', _("Silence")),
        ('white-noise', _("White uniform noise")),
        ('pink-noise', _("Pink noise")),
        ('sine-table', _("Sine table")),
        ('ticks', _("Periodic Ticks")),
        ('gaussian-noise', _("White Gaussian noise")),
    )

    fallback = models.CharField(max_length=255,
        choices=WAVE, default=WAVE[0][0])    

#    def save(self, force_insert=False, force_update=False):
#        super(Stream, self).save(force_insert, force_update)

class SourcedStream(Stream):
    user = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)

class RecodedStream(Stream):
    source = models.ForeignKey(Stream, related_name='recoded')
    
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, related_name="profile")
    htdigest = models.CharField(max_length=255, blank=True)

    def set_htdigest(self, password, realm="Default Realm"):
        string = "%s:%s:%s" % (self.user.username, realm, password)
        hash = hashlib.md5(string).hexdigest()
        self.htdigest = "%s:%s:%s" % (self.user.username, realm, hash)
        self.save()


class Status(models.Model):
    name = models.CharField(max_length=100)
    status = models.PositiveSmallIntegerField()
    verbose_status = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    category = models.CharField(max_length=100)
    step = models.PositiveIntegerField()

    def value(self):
        import datetime
        now = datetime.datetime.now()
        diff = now - self.timestamp
        return ((diff.seconds - self.step) * 1.0 / self.step)

    def __unicode__(self):
        return u"<Status for %s>" % self.name


from django.db.models.signals import post_save
def saved(sender, instance, created, **kwargs):
    print "Saved (models.py:314): ", sender, repr(instance)


post_save.connect(saved, Show)
post_save.connect(saved, ShowFeed)
post_save.connect(saved, Episode)
post_save.connect(saved, EpisodePart)
post_save.connect(saved, Graphic)
post_save.connect(saved, Recording)
post_save.connect(saved, StreamSetup)
post_save.connect(saved, Stream)
post_save.connect(saved, SourcedStream)
post_save.connect(saved, RecodedStream)
post_save.connect(saved, UserProfile)
post_save.connect(saved, Status)
