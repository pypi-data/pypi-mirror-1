from django.contrib.syndication.feeds import Feed
from django.utils import feedgenerator
from django.core.urlresolvers import reverse
from models import Article
import settings

class RssRecentArticlesFeed(Feed):
    feed_title = getattr(settings, 'NEWS_FEED_TITLE', 'Recent articles')
    feed_description = getattr(settings, 'NEWS_FEED_DESCRIPTION', 'Recent articles')
    feed_link = getattr(settings, 'NEWS_FEED_LINK', '/news/')

    feed_type = feedgenerator.Rss201rev2Feed

    title_template = 'feeds/title.html'
    description_template = 'feeds/description.html'

    title = feed_title
    description = feed_description
    link = feed_link

    def items(self):
        return Article.recent.all()