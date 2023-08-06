import time
from warnings import warn
import pylons
from pylons import request
from pylons.controllers import *
from pylons.controllers.util import redirect_to
from bel.lib.base import *
from bel.model import *
import bel.lib.helpers as h
from pylons.templating import render_mako

import logging
log = logging.getLogger(__name__)

class FeedControllerBase(BaseController):
    """ Object for generating feeds in multiple formats """

    def __init__(self, default="atom1.0"):
        self.default = default
        self.formats = ["atom1.0", "rss2.0"]

    def date_to_3339(self, date):
        date = date.strftime("%Y-%m-%dT%H:%M:%SZ")
        return date

    def date_to_822(self, date):
        date = date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        return date
    
    def depr_entrys(self, feed):
        if "entrys" in feed:
            warn("You should use 'entries' instead of 'entrys'",
                DeprecationWarning, 3)
            feed['entries'] = feed['entrys']
            del feed['entrys']

    def format_dates(self, feed, format):
        if format == 822:
            convert_date = self.date_to_822
        else:
            convert_date = self.date_to_3339
        if feed.has_key('updated'):
            feed["updated"] = convert_date(feed["updated"])
        self.depr_entrys(feed)
        for entry in feed['entries']:
            if entry.has_key('updated'):
                entry["updated"] = convert_date(entry["updated"])
            if entry.has_key('published'):
                entry["published"] = convert_date(entry["published"])
        return feed

    def index(self):
        return redirect_to("%s" % self.default)

    def atom1_0(self, **kwargs):
        feed = self.get_feed_data(**kwargs)
        self.format_dates(feed, 3339)
        feed["href"] = "%s/" % feed['feedmeta']['link']
        self.depr_entrys(feed)
        c.feedmeta = feed['feedmeta']
        c.entries = feed['entries']
        return render("feed/atom1_0.mak")
                        # ,
                        # content_type="application/atom+xml", 
                        # feed)

    def rss2_0(self, **kwargs):
        feed = self.get_feed_data(**kwargs)
        self.format_dates(feed, 822)
        self.depr_entrys(feed)
        c.feedmeta = feed['feedmeta']
        c.entries = feed['entries']
        return render("feed/rss2_0.mak")
                               #  ,
                               # content_type="application/rss+xml", 
                               # feed)
