import foaflib.helpers.blog as blog
from foaflib.helpers.delicious import Delicious
from foaflib.helpers.identica import Identica
from foaflib.helpers.twitter_ import Twitter

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
