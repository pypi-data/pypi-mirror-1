from foaflib.helpers.basehelper import BaseHelper
from foaflib.utils.activitystreamevent import ActivityStreamEvent

class Twitter(BaseHelper):

    def __init__(self):
        BaseHelper.__init__(self)
        try:
            import twitter
            self.twitter = twitter
            import time
            self.time = time
            self._supported = True
        except ImportError:
            self._supported = False

    def _accept_account(self, account):
        return "twitter.com" in account.accountServiceHomepage

    def _handle_account(self, account):
        if account.accountName:
            username = account.accountName
        elif account.accountProfilePage:
            username = account.accountProfilePage.split("/")[-1]
        elif account.accountServiceHomepage:
            username = account.accountServiceHomepage.split("/")[-1]
        else:
            return []

        api = self.twitter.Api()
        tweets = []
        for tweet in api.GetUserTimeline(username):
            event = ActivityStreamEvent()
            event.type = "Twitter"
            event.detail = tweet.text
            event.link = "http://www.twitter.com/%s/status/%d" % (username, tweet.id)
            event.timestamp = self.time.strptime(tweet.created_at, "%a %b %d %H:%M:%S +0000 %Y")
            tweets.append(event)
        return tweets
