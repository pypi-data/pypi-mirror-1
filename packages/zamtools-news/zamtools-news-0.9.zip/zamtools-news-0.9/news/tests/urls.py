from django.conf.urls.defaults import *
from ..models import Article
import settings

num_latest = 10

urlpatterns = patterns('news.views',
    url(r'^news/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[\-\d\w]+)/$', 'detail', {}, name='news_detail'),
    url(r'^news/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'day', {}, name='news_day'),
    url(r'^news/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'month', {}, name='news_month'),
    url(r'^news/(?P<year>\d{4})/$', 'year', {}, name='news_year'),
    url(r'^news/$', 'index', {}, name='news_index'),
)