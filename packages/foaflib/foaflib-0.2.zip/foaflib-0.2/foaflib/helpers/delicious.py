from foaflib.helpers.basehelper import BaseHelper
from foaflib.utils.activitystreamevent import ActivityStreamEvent

class Delicious(BaseHelper):

    def __init__(self):

        try:
            import feedparser
            self.feedparser = feedparser
            self._supported = True
        except ImportError:
            self._supported = False

    def _accept_account(self, account):

        homepage = account.accountServiceHomepage
        return "del.icio.us" in homepage or "delicious.com" in homepage

    def _handle_account(self, account):

        events = []
        username = account.accountName
        if not username:
            return events
        feed_url = "http://feeds.delicious.com/v2/rss/%s?count=15" % username
        entries = self.feedparser.parse(feed_url)["entries"]
        for entry in entries:
            event = ActivityStreamEvent()
            event.type = "Del.icio.us"
            event.detail = "Bookmarked: %s" % entry.title
            event.link = entry.link
            event.timestamp = entry.updated_parsed
            events.append(event)
        return events 
