from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.db.models import Q
from django_htmx.http import HttpResponseClientRefresh
from crawler.models import CrawlRun, LogEntry
from decklist.models import Deck, SiteStat


@login_required
def crawler_index(request):
    runs = CrawlRun.objects.order_by('-crawl_start_time')
    paginator = Paginator(runs, 8, orphans=3)
    page_number = request.GET.get('page')
    runs_page = paginator.get_page(page_number)

    try:
        stats = SiteStat.objects.latest()
    except SiteStat.DoesNotExist:
        stats = None

    return render(
        request,
        'crawler/index.html',
        {
            'runs': runs_page,
            'stats': stats,
        },
    )


@login_required
def run_detail(request, run_id):
    run = get_object_or_404(CrawlRun, pk=run_id)

    return render(
        request,
        'crawler/run_detail.html',
        {
            'run': run,
            'errored': run.state == CrawlRun.State.ERROR,
            'allow_search_infinite': run.state == CrawlRun.State.NOT_STARTED and run.search_back_to,
            'can_cancel': run.state not in (CrawlRun.State.CANCELLED, CrawlRun.State.COMPLETE),
        },
    )


@login_required
@require_POST
def run_remove_error_hx(request, run_id):
    run = get_object_or_404(CrawlRun, pk=run_id)

    if run.state == run.State.ERROR:
        if run.next_fetch:
            run.state = run.State.FETCHING_DECKS
        else:
            run.state = run.State.NOT_STARTED
        run.save()
    
    return HttpResponseClientRefresh()


@login_required
@require_POST
def run_remove_limit_hx(request, run_id):
    run = get_object_or_404(CrawlRun, pk=run_id)

    if run.state == run.State.NOT_STARTED:
        run.search_back_to = None
        run.save()
    
    return HttpResponseClientRefresh()


@login_required
@require_POST
def run_cancel_hx(request, run_id):
    run = get_object_or_404(CrawlRun, pk=run_id)

    if run.state != CrawlRun.State.COMPLETE:
        run.state = CrawlRun.State.CANCELLED
        run.save()
    
    return HttpResponseClientRefresh()


@login_required
@require_POST
def update_stats(request):
    legal_decks = (
        Deck.objects
        .filter(pdh_legal=True)
        .count()
    )

    s = SiteStat(legal_decks=legal_decks)
    s.save()
    
    return HttpResponseClientRefresh()


@login_required
def log_index(request):
    logs = (
        LogEntry.objects
        .filter(follows=None)
    )
    paginator = Paginator(logs, 10, orphans=3)
    page_number = request.GET.get('page')
    logs_page = paginator.get_page(page_number)

    return render(
        request,
        'crawler/log_index.html',
        {
            'logs': logs_page,
        },
    )


@login_required
def log_from(request, start_log):
    # brute force is best force 💪
    # yes this is gross, but "reversing a linked list" in SQL
    # turns out to be a bad idea.
    logs = (
        LogEntry.objects
        .filter(
            Q(id=start_log) |
            Q(follows__id=start_log) |
            Q(follows__follows__id=start_log) |
            Q(follows__follows__follows__id=start_log) |
            Q(follows__follows__follows__follows__id=start_log) |
            Q(follows__follows__follows__follows__follows__id=start_log) |
            Q(follows__follows__follows__follows__follows__follows__id=start_log) |
            Q(follows__follows__follows__follows__follows__follows__follows__id=start_log) |
            Q(follows__follows__follows__follows__follows__follows__follows__follows__id=start_log) |
            Q(follows__follows__follows__follows__follows__follows__follows__follows__follows__id=start_log)
        )
        .order_by('created')
    )

    template = 'crawler/log.html'
    if request.htmx:
        template = 'crawler/log_partial.html'

    return render(
        request,
        template,
        {
            'logs': logs,
        },
    )
