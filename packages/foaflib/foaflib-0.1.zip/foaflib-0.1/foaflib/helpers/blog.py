from foaflib.utils.activitystreamevent import ActivityStreamEvent

try:
    from urllib import urlopen
    from urlparse import urljoin
    from BeautifulSoup import BeautifulSoup
    from feedparser import parse
    _CAN_DO_ = True
except ImportError:
    _CAN_DO_ = False

def get_latest(foafprofile):
    entries = []

    if not _CAN_DO_:
        return entries

    for blog in foafprofile.weblogs:
        u = urlopen(blog)
        blogpage = u.read()
        u.close()

        try:
            bs = BeautifulSoup(blogpage)
            feeds = bs.findAll("link",{"type":"application/rss+xml"})
            for feed in feeds:
                try:
                    feed_url = urljoin(blog, feed["href"])
                    feedentries = []
                    for entry in parse(feed_url)["entries"]:
                        event = ActivityStreamEvent()
                        event.type = "Blog post"
                        event.detail = entry["title"]
                        if "published_parsed" in entry:
                            event.timestamp = entry["published_parsed"]
                        if "updated_parsed" in entry:
                            event.timestamp = entry["updated_parsed"]
                        feedentries.append(event)
                    entries.extend(feedentries)
                    break
                except:
                    continue
        except:
            continue
    return entries
