import re
import feedparser
import time
import itertools
import string

from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import getUtility

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from plone.memoize import request
from plone.memoize.interfaces import ICacheChooser

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.accuweather import AccuWeatherMessageFactory as _

CITY_REGEX = re.compile(r'(.+?)\s?[,(]')
ICON_REGEX = re.compile(r'/(\d+)_\S+\.gif')
TEMP_REGEX = re.compile(r'.+\: (\d.*[CF])')

class IAccuWeather(IPortletDataProvider):
    
    metric = schema.Bool(
            title=_(u"Use metric temperature values"),
            default=True
        )
    
    locations = schema.List(
            title=_(u"Location codes"),
            description=_(u"AccuWeather location codes, one per line. For example OCN|AU|WA|PERTH"),
            value_type=schema.ASCIILine(),
        )
    
    cache_timeout = schema.Int(
            title=_(u"Maximum time to cache feed data"),
            default=900,
        )


class Assignment(base.Assignment):
    implements(IAccuWeather)

    metric = True
    locations = []
    cache_timeout = 900

    def __init__(self, metric=True, locations=[], cache_timeout=900):
        self.metric = metric
        self.locations = locations
        self.cache_timeout = cache_timeout

    title = _(u"Weather")

class Renderer(base.Renderer):
    render = ViewPageTemplateFile('accuweather.pt')
        
    def cleanFeed(self, feed):
        """Sanitize the feed.

        This function makes sure all feed and entry data we depend on us
        present and in proper form.
        """
        for entry in feed.entries:
            entry["feed"]=feed.feed
            if not "published_parsed" in entry:
                entry["published_parsed"]=entry["updated_parsed"]
                entry["published"]=entry["updated"]

    def getFeed(self, url):
        """Fetch a feed.

        This may return a cached result if the cache entry is considered to
        be fresh. Returned feeds have been cleaned using the cleanFeed method.
        """
        now=time.time()

        chooser=getUtility(ICacheChooser)
        cache=chooser("collective.portlet.accuweather.RSSCache")

        cached_data=cache.get(url, None)
        if cached_data is not None:
            (timestamp, feed)=cached_data
            if now-timestamp<self.data.cache_timeout:
                return feed

            newfeed=feedparser.parse(url,
                    etag=getattr(feed, "etag", None),
                    modified=getattr(feed, "modified", None))
            
            status = 304
            try:
                status = newfeed.status
            except AttributeError:
                # try to get from cache if feed was empty
                pass
            
            if status == 304:
                self.cleanFeed(feed)
                cache[url]=(now+self.data.cache_timeout, feed)
                return feed

        feed=feedparser.parse(url)
        self.cleanFeed(feed)
        cache[url]=(now+self.data.cache_timeout, feed)

        return feed

    @request.cache(get_key=lambda func,self:self.data.locations, get_request="self.request")
    def entries(self):
        """Get entries for the portlet. A list of dicts.
        """
        
        merged = []
        
        metric = 1
        if not self.data.metric:
            metric = 0
        
        for location in self.data.locations:
            url = "http://rss.accuweather.com/rss/liveweather_rss.asp?metric=%d&locCode=%s" % (metric, location,)
            feed = self.getFeed(url)
            if feed is None:
                continue
            
            city = ''
            current_weather = ''
            icon_number = ''
            temp = ''
            
            city = feed.feed.get('title', '')
            city_match = CITY_REGEX.search(city)
            if city_match:
                city = string.capwords(city_match.group(1))
            
            entries = feed.entries
            if entries:
                title = entries[0].get('title', '')
                current_weather = title.replace('Currently: ', '')
                
                temp_match = TEMP_REGEX.search(current_weather)
                if temp_match:
                    temp = temp_match.group(1)
                
                summary = entries[0].get('summary', '')
                
                icon_match = ICON_REGEX.search(summary)
                if icon_match:
                    icon_number = icon_match.group(1)
                
            merged.append({'id': location.replace('|', '-'),
                           'location': location,
                           'city': city,
                           'current': current_weather,
                           'icon_number': icon_number,
                           'temp': temp})
        
        return merged

class AddForm(base.AddForm):
    form_fields = form.Fields(IAccuWeather)
    
    label = _(u"Add AccuWeather Portlet")
    description = _(u"This portlet display the current weather for one or more locations, based on an AccuWeather.com RSS feed.")
    
    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IAccuWeather)
    
    label = _(u"Edit AccuWeather Portlet")
    description = _(u"This portlet display the current weather for one or more locations, based on an AccuWeather.com RSS feed.")
