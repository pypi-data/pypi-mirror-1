from django.conf.urls.defaults import *
from feeds import RssRecentArticlesFeed
import settings

urlpatterns = patterns('news.views',
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[\-\d\w]+)/$', 'detail', {}, name='news_detail'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'day', {}, name='news_day'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'month', {}, name='news_month'),
    url(r'^(?P<year>\d{4})/$', 'year', {}, name='news_year'),
    url(r'^$', 'index', {}, name='news_index'),
)

feeds = {
    'recent':RssRecentArticlesFeed,
}

urlpatterns += patterns('django.contrib.syndication.views',
    (r'^feeds/(?P<url>.*)/$', 'feed', {'feed_dict': feeds}),
)