from foaflib.utils.activitystreamevent import ActivityStreamEvent

class BaseHelper(object):

    def __init__(self):
        self._supported = False

    def _accept_account(self, onlineaccount):
        return False

    def _handle_account(self, onlineaccount):
        return None

    def get_latest(self, foafperson):
        if not self._supported:
            return []
        events = []
        for account in foafperson.accounts:
            if self._accept_account(account):
                account_events = self._handle_account(account)
                account_events = filter(lambda x: isinstance(x, ActivityStreamEvent), account_events)
                events.extend(account_events)
        return events
