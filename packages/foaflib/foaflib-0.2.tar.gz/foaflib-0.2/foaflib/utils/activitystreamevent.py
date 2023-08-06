class ActivityStreamEvent(object):

    def __init__(self):
        self.type = ""
        self.detail = ""
        self.link = ""
        self.timestamp = None

    def __cmp__(self, other):

        return cmp(self.timestamp, other.timestamp)
