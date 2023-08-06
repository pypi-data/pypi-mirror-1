from django.test import TestCase
from ..models import Article
from django.contrib.auth.models import User
from datetime import date
import settings

class PublicTests(TestCase):
    """
    Tests the public methods in the model and the context returned by the views.
    """
    def setUp(self):
        settings.NEWS_NUM_RECENT = 10
        self.articles = []
        for i in range(1,5):
            article = Article.objects.create(title='Public %s' % i, body='Public', author=None, is_public=True)
            article.date_created = date(2009, 1, i)
            article.save()
            self.articles.append(article)
        # non public article
        article = Article.objects.create(title='Private', body='Not Public', author=None, is_public=False)
        article.date_created = date(2009, 1, 6)
        article.save()
        self.articles.append(article)

    def tearDown(self):
        for article in self.articles:
            article.delete()

    def test_public_manager(self):
        articles = Article.public.all()
        self.assertEqual(list(articles), [self.articles[3], self.articles[2], self.articles[1], self.articles[0]])

    def test_public_context(self):
        response = self.client.get('/news/')
        articles = response.context[0]['articles']
        self.assertEqual(list(articles), [self.articles[3], self.articles[2], self.articles[1], self.articles[0]])

class RecentTests(TestCase):
    """
    Tests year based views.
    """
    def setUp(self):
        settings.NEWS_NUM_RECENT = 2
        self.articles = []
        for i in range(1,5):
            article = Article.objects.create(title='Public %s' % i, body='Public', author=None, is_public=True)
            article.date_created = date(2009, 1, i)
            article.save()
            self.articles.append(article)

    def tearDown(self):
        for article in self.articles:
            article.delete()

    def test_recent_manager(self):
        articles = Article.recent.all()
        self.assertEqual(list(articles), [self.articles[3], self.articles[2]])

    def test_recent_context(self):
        response = self.client.get('/news/')
        articles = response.context[0]['articles']
        self.assertEqual(list(articles), [self.articles[3], self.articles[2]])

class YearTests(TestCase):
    """
    Tests year based views.
    """
    urls = 'news.tests.urls'

    def setUp(self):
        self.current_article = Article.objects.create(title='current', body='Public', author=None, is_public=True)
        self.current_article.date_created = date(2009, 1, 1)
        self.current_article.save()
        self.previous_date = date(2008, 1, 1)
        self.previous_article = Article.objects.create(title='previous', body='Public', author=None, is_public=True)
        self.previous_article.date_created = self.previous_date
        self.previous_article.save()
        self.next_date = date(2010, 1, 1)
        self.next_article = Article.objects.create(title='next', body='Public', author=None, is_public=True)
        self.next_article.date_created = self.next_date
        self.next_article.save()
        self.articles = [self.current_article, self.previous_article, self.next_article]

    def tearDown(self):
        for article in self.articles:
            article.delete()

    def test_current_year(self):
        response = self.client.get('/news/2009/')
        articles = response.context[0]['articles']
        self.assertEqual(list(articles), [self.current_article])

    def test_previous_year(self):
        response = self.client.get('/news/2009/')
        previous_date = response.context[0]['previous_date']
        self.assertEqual(previous_date, self.previous_date)

    def test_next_year(self):
        response = self.client.get('/news/2009/')
        next_date = response.context[0]['next_date']
        self.assertEqual(next_date, self.next_date)

class MonthTests(TestCase):
    """
    Tests month based views.
    """
    urls = 'news.tests.urls'

    def setUp(self):
        self.current_article = Article.objects.create(title='current', body='Public', author=None, is_public=True)
        self.current_article.date_created = date(2009, 5, 1)
        self.current_article.save()
        self.previous_date = date(2009, 4, 1)
        self.previous_article = Article.objects.create(title='previous', body='Public', author=None, is_public=True)
        self.previous_article.date_created = self.previous_date
        self.previous_article.save()
        self.next_date = date(2009, 6, 1)
        self.next_article = Article.objects.create(title='next', body='Public', author=None, is_public=True)
        self.next_article.date_created = self.next_date
        self.next_article.save()
        self.articles = [self.current_article, self.previous_article, self.next_article]

    def tearDown(self):
        for article in self.articles:
            article.delete()

    def test_current_month(self):
        response = self.client.get('/news/2009/5/')
        articles = response.context[0]['articles']
        self.assertEqual(list(articles), [self.current_article])

    def test_previous_month(self):
        response = self.client.get('/news/2009/5/')
        previous_date = response.context[0]['previous_date']
        self.assertEqual(previous_date, self.previous_date)

    def test_next_month(self):
        response = self.client.get('/news/2009/5/')
        next_date = response.context[0]['next_date']
        self.assertEqual(next_date, self.next_date)

class DayTests(TestCase):
    """
    Tests day based views.
    """
    def setUp(self):
        self.current_article = Article.objects.create(title='current', body='Public', author=None, is_public=True)
        self.current_article.date_created = date(2009, 1, 5)
        self.current_article.save()
        self.previous_date = date(2009, 1, 4)
        self.previous_article = Article.objects.create(title='previous', body='Public', author=None, is_public=True)
        self.previous_article.date_created = self.previous_date
        self.previous_article.save()
        self.next_date = date(2009, 1, 6)
        self.next_article = Article.objects.create(title='next', body='Public', author=None, is_public=True)
        self.next_article.date_created = self.next_date
        self.next_article.save()
        self.articles = [self.current_article, self.previous_article, self.next_article]

    def tearDown(self):
        for article in self.articles:
            article.delete()

    def test_current_day(self):
        response = self.client.get('/news/2009/1/5/')
        articles = response.context[0]['articles']
        self.assertEqual(list(articles), [self.current_article])

    def test_previous_day(self):
        response = self.client.get('/news/2009/1/5/')
        previous_date = response.context[0]['previous_date']
        self.assertEqual(previous_date, self.previous_date)

    def test_next_day(self):
        response = self.client.get('/news/2009/1/5/')
        next_date = response.context[0]['next_date']
        self.assertEqual(next_date, self.next_date)

class DayTests(TestCase):
    """
    Tests detail based views.
    """
    urls = 'news.tests.urls'

    def setUp(self):
        self.current_article = Article.objects.create(title='current', body='Public', author=None, is_public=True)
        self.current_article.date_created = date(2009, 1, 5)
        self.current_article.save()
        self.previous_date = date(2009, 1, 4)
        self.previous_article = Article.objects.create(title='previous', body='Public', author=None, is_public=True)
        self.previous_article.date_created = self.previous_date
        self.previous_article.save()
        self.next_date = date(2009, 1, 6)
        self.next_article = Article.objects.create(title='next', body='Public', author=None, is_public=True)
        self.next_article.date_created = self.next_date
        self.next_article.save()
        self.articles = [self.current_article, self.previous_article, self.next_article]

    def tearDown(self):
        for article in self.articles:
            article.delete()

    def test_current_article(self):
        response = self.client.get('/news/2009/1/5/current/')
        articles = response.context[0]['articles']
        self.assertEqual(list(articles), [self.current_article])