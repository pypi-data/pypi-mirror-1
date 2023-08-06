from foaflib.utils.activitystreamevent import ActivityStreamEvent
from foaflib.helpers.basehelper import BaseHelper

class Identica(BaseHelper):

    def __init__(self):
        BaseHelper.__init__(self)
        try:
            import feedparser
            self.feedparser = feedparser
            self._supported = True
        except ImportError:
            self._supported = False

    def _accept_account(self, account):
        return "identi.ca" in account.accountServiceHomepage

    def _handle_account(self, account):

        events = []
        username = account.accountName
        if not username:
            return events
        url = "https://identi.ca/api/statuses/user_timeline/%s.atom" % username
        try:
            feedentries = self.feedparser.parse(url)["entries"]
            for entry in feedentries:
                event = ActivityStreamEvent()
                event.type = "Identi.ca"
                event.detail = entry["title"]
                event.link = entry["link"]
                event.timestamp = entry["published_parsed"]
                events.append(event)
        except:
            pass
        return events
