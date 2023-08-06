from models import Article
from django.shortcuts import render_to_response
from django.template import RequestContext
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator
from datetime import date
import settings

page_size = getattr(settings, 'NEWS_PAGE_SIZE', 10)

def index(request, extra_context={}, template_name='news/article_archive.html'):
    """
    Returns a list of the recent public articles.
    """
    articles = Article.recent.all()
    paginator = Paginator(articles, page_size)
    page_num = request.GET.get('page', 1)
    page = paginator.page(page_num)
    return render_to_response(
        template_name,
        {
            'articles':articles,
            'page':page,
        },
        context_instance=RequestContext(request, extra_context)
    )
    

def year(request, year, extra_context={}, template_name='news/article_archive_year.html'):
    """
    Returns a list of public articles that belong to the supplied year.
    """
    year = int(year)

    articles = Article.public.filter(date_created__year=year)
    paginator = Paginator(articles, page_size)
    page_num = request.GET.get('page', 1)
    page = paginator.page(page_num)
    current_date = date(year, 1, 1)

    # if no articles exist for previous_date make it None
    previous_date = current_date + relativedelta(years=-1)
    if not Article.public.filter(date_created__year=previous_date.year):
        previous_date = None
    
    # if no articles exist for next_date make it None
    next_date = current_date + relativedelta(years=+1)
    if not Article.public.filter(date_created__year=next_date.year):
        next_date = None

    return render_to_response(
        template_name,
        {
            'articles':articles,
            'page':page,
            'current_date':current_date,
            'previous_date':previous_date,
            'next_date':next_date,
        },
        context_instance=RequestContext(request, extra_context)
    )

def month(request, year, month, extra_context={}, template_name='news/article_archive_month.html'):
    """
    Returns a list of public articles that belong to the supplied year and 
    month.
    """
    year = int(year)
    month = int(month)

    articles = Article.public.filter(date_created__year=year, date_created__month=month)
    paginator = Paginator(articles, page_size)
    page_num = request.GET.get('page', 1)
    page = paginator.page(page_num)
    current_date = date(year, month, 1)

    # if no articles exist for previous_date make it None
    previous_date = current_date + relativedelta(months=-1)
    if not Article.public.filter(date_created__year=previous_date.year, date_created__month=previous_date.month):
        previous_date = None
    
    # if no articles exist for next_date make it None
    next_date = current_date + relativedelta(months=+1)
    if not Article.public.filter(date_created__year=next_date.year, date_created__month=next_date.month):
        next_date = None

    return render_to_response(
        template_name,
        {
            'articles':articles,
            'page':page,
            'current_date':current_date,
            'previous_date':previous_date,
            'next_date':next_date,
        },
        context_instance=RequestContext(request, extra_context)
    )

def day(request, year, month, day, extra_context={}, template_name='news/article_archive_day.html'):
    """
    Returns a list of public articles that belong to the supplied year, 
    month and day.
    """
    year = int(year)
    month = int(month)
    day = int(day)
    
    articles = Article.public.filter(date_created__year=year, date_created__month=month, date_created__day=day)
    paginator = Paginator(articles, page_size)
    page_num = request.GET.get('page', 1)
    page = paginator.page(page_num)
    current_date = date(year, month, day)

    # if no articles exist for previous_date make it None
    previous_date = current_date + relativedelta(days=-1)
    if not Article.public.filter(date_created__year=previous_date.year, date_created__month=previous_date.month, date_created__day=previous_date.day):
        previous_date = None
    
    # if no articles exist for next_date make it None
    next_date = current_date + relativedelta(days=+1)
    if not Article.public.filter(date_created__year=next_date.year, date_created__month=next_date.month, date_created__day=next_date.day):
        next_date = None

    return render_to_response(
        template_name,
        {
            'articles':articles,
            'page':page,
            'current_date':current_date,
            'previous_date':previous_date,
            'next_date':next_date,
        },
        context_instance=RequestContext(request, extra_context)
    )

def detail(request, year, month, day, slug, extra_context={}, template_name='news/article_detail.html'):
    """
    Returns a single article based on the supplied year, month, day and slug.
    """
    year = int(year)
    month = int(month)
    day = int(day)

    articles = Article.public.filter(date_created__year=year, date_created__month=month, date_created__day=day, slug=slug)
    paginator = Paginator(articles, page_size)
    page_num = request.GET.get('page', 1)
    page = paginator.page(page_num)
    current_date = date(year, month, day)
    current_date = date(year, month, day)

    return render_to_response(
        template_name,
        {
            'articles':articles,
            'page':page,
            'current_date':current_date,
        },
        context_instance=RequestContext(request, extra_context)
    )

def rss_recent(request):
    pass