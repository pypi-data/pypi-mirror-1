import foaflib.helpers.blog as blog
from foaflib.helpers.delicious import Delicious
from foaflib.helpers.identica import Identica
from foaflib.helpers.twitter_ import Twitter

try:
    from feedformatter import Feed
    _CAN_DO_FEEDS_ = True
except ImportError:
    _CAN_DO_FEEDS_ = False

_ALL_HELPERS_ = [Delicious]
_ALL_HELPERS_.append(Identica)
_ALL_HELPERS_.append(Twitter)

class ActivityStream(object):

    def __init__(self, foafperson):
        self.person = foafperson
        self.helpers = []
        for helper in _ALL_HELPERS_:
            self.helpers.append(helper())
            
    def get_latest_events(self, count=10):
        events = []
        events.extend(blog.get_latest(self.person))
        for helper in self.helpers:
            events.extend(helper.get_latest(self.person))
        events.sort()
        events.reverse()
        return events[0:count]

    def build_feed(self):
        if not _CAN_DO_FEEDS_:
            return None
        feed = Feed()
        feed.feed["title"] = self.person.name + "'s Activity Stream"
        feed.feed["description"] = self.person.name + "'s Activity Stream"
        feed.feed["link"] = self.person.uri
        feed.feed["author"] = self.person.name
        for event in self.get_latest_events():
            item = {}
            item["title"] = event.type + " - " + event.detail
            item["pubDate"] = event.timestamp
            item["link"] = event.link
            item["guid"] = event.link
            feed.items.append(item)
        return feed
