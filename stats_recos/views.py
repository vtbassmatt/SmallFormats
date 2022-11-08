from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.core.paginator import Paginator
from decklist.models import Card, Deck, Printing, CardInDeck
from .wubrg_utils import COLORS
import operator
import functools


_CARDS_LINKS = (
    ('Top cards', reverse_lazy('card-top')),
    ('All cards', reverse_lazy('card')),
 )
_CMDRS_LINKS = (
    ('Top commanders', reverse_lazy('cmdr-top')),
    ('All commanders', reverse_lazy('cmdr')),
 )
_LANDS_LINKS = (
    ('Top lands', reverse_lazy('land-top')),
    ('All lands ', reverse_lazy('land')),
 )
_LINKS = (
    # menu? title    link or menu items
    (True,  'Cards', _CARDS_LINKS),
    (True,  'Commanders', _CMDRS_LINKS),
    (True,  'Lands', _LANDS_LINKS),
    (False, 'Partner decks', reverse_lazy('partner-decks')),
)

def _deck_count_exact_color(w, u, b, r, g):
    return (
        CardInDeck.objects
        .filter(is_pdh_commander=True)
        .aggregate(count=(
            Count('deck',
            filter=
                Q(card__identity_w=w) & 
                Q(card__identity_u=u) &
                Q(card__identity_b=b) &
                Q(card__identity_r=r) &
                Q(card__identity_g=g),
            distinct=True,
            ))
        )
    )['count']


def _deck_count_at_least_color(w, u, b, r, g):
    if not any([w, u, b, r, g]):
        return Deck.objects.count()

    # build up a filter for the aggregation
    # that has a Q object set to True for each color we
    # care about and nothing for the colors which we don't
    q_objs = []
    for c in 'wubrg':
        if locals()[c]:
            key = f'card__identity_{c}'
            q_objs.append(Q(**dict([(key,True),])))
    filter_q = functools.reduce(operator.and_, q_objs)

    return (
        CardInDeck.objects
        .filter(is_pdh_commander=True)
        .aggregate(count=Count('deck', filter=filter_q, distinct=True))
    )['count']


def stats_index(request):
    return render(
        request,
        "index.html",
        context={
            'links': _LINKS,
        },
    )


def partner_decks(request):
    partner_decks = (
        Deck.objects
        .annotate(num_cmdrs=Count(
            'card_list', filter=Q(card_list__is_pdh_commander=True)
        ))
        .filter(num_cmdrs__gt=1)
    )
    paginator = Paginator(partner_decks, 25, orphans=3)
    page_number = request.GET.get('page')
    decks_page = paginator.get_page(page_number)

    return render(
        request,
        "partner_decks.html",
        context={
            'decks': decks_page,
            'links': _LINKS,
        },
    )


def commander_index(request):
    return render(
        request,
        "commander_index.html",
        context={
            'colors': [
                (c[0], f'cmdr-{c[0]}') for c in COLORS
            ],
            'links': _LINKS,
        },
    )


def top_commanders(request):
    cmdr_cards = (
        Card.objects
        .filter(deck_list__is_pdh_commander=True)
        .annotate(num_decks=Count('deck_list'))
        .order_by('-num_decks')
    )
    deck_count = Deck.objects.count()
    paginator = Paginator(cmdr_cards, 25, orphans=3)
    page_number = request.GET.get('page')
    cards_page = paginator.get_page(page_number)

    return render(
        request,
        "commanders.html",
        context={
            'cards': cards_page,
            'deck_count': deck_count,
            'links': _LINKS,
        },
    )


def commanders_by_color(request, w=False, u=False, b=False, r=False, g=False):
    cmdrs = (
        Card.objects
        .prefetch_related('printings')
        .filter(
            identity_w=w,
            identity_u=u,
            identity_b=b,
            identity_r=r,
            identity_g=g,
        )
        .filter(
            # TODO: banlist? silver cards which say "Summon"?
            # TODO: backgrounds
            type_line__contains='Creature',
            printings__rarity=Printing.Rarity.UNCOMMON,
        )
        .annotate(num_decks=Count(
            'deck_list',
            distinct=True,
            filter=Q(deck_list__is_pdh_commander=True)
        ))
        .filter(num_decks__gt=0)
        .order_by('-num_decks')
    )
    paginator = Paginator(cmdrs, 25, orphans=3)
    page_number = request.GET.get('page')
    cards_page = paginator.get_page(page_number)

    return render(
        request,
        "commanders.html",
        context={
            'cards': cards_page,
            # TODO: probably fails to account for partners
            'deck_count': _deck_count_exact_color(w, u, b, r, g),
            'links': _LINKS,
        },
    )


def land_index(request):
    return render(
        request,
        "land_index.html",
        context={
            'colors': [
                (c[0], f'land-{c[0]}') for c in COLORS
            ],
            'links': _LINKS,
        },
    )


def top_lands(request):
    land_cards = (
        Card.objects
        .filter(type_line__contains='Land')
        .annotate(num_decks=Count('deck_list'))
        .order_by('-num_decks')
        .filter(num_decks__gt=0)
    )
    deck_count = Deck.objects.count()
    paginator = Paginator(land_cards, 25, orphans=3)
    page_number = request.GET.get('page')
    cards_page = paginator.get_page(page_number)

    return render(
        request,
        "lands.html",
        context={
            'cards': cards_page,
            'deck_count': deck_count,
            'links': _LINKS,
        },
    )


def lands_by_color(request, w=False, u=False, b=False, r=False, g=False):
    land_cards = (
        Card.objects
        .filter(
            type_line__contains='Land',
            identity_w=w,
            identity_u=u,
            identity_b=b,
            identity_r=r,
            identity_g=g,
        )
        .annotate(num_decks=Count('deck_list'))
        .order_by('-num_decks')
        .filter(num_decks__gt=0)
    )
    paginator = Paginator(land_cards, 25, orphans=3)
    page_number = request.GET.get('page')
    cards_page = paginator.get_page(page_number)

    return render(
        request,
        "lands.html",
        context={
            'cards': cards_page,
            'deck_count': _deck_count_at_least_color(w, u, b, r, g),
            'links': _LINKS,
        },
    )


def card_index(request):
    return render(
        request,
        "card_index.html",
        context={
            'colors': [
                (c[0], f'card-{c[0]}') for c in COLORS
            ],
            'links': _LINKS,
        },
    )


def top_cards(request):
    cards = (
        Card.objects
        .annotate(num_decks=Count('deck_list'))
        .filter(num_decks__gt=0)
        .order_by('-num_decks')
    )
    deck_count = Deck.objects.count()
    paginator = Paginator(cards, 25, orphans=3)
    page_number = request.GET.get('page')
    cards_page = paginator.get_page(page_number)

    return render(
        request,
        "cards.html",
        context={
            'cards': cards_page,
            'deck_count': deck_count,
            'links': _LINKS,
        },
    )


def cards_by_color(request, w=False, u=False, b=False, r=False, g=False):
    cards = (
        Card.objects
        .filter(
            identity_w=w,
            identity_u=u,
            identity_b=b,
            identity_r=r,
            identity_g=g,
        )
        .annotate(num_decks=Count('deck_list'))
        .order_by('-num_decks')
        .filter(num_decks__gt=0)
    )
    paginator = Paginator(cards, 25, orphans=3)
    page_number = request.GET.get('page')
    cards_page = paginator.get_page(page_number)

    return render(
        request,
        "cards.html",
        context={
            'cards': cards_page,
            'deck_count': _deck_count_at_least_color(w, u, b, r, g),
            'links': _LINKS,
        },
    )


def single_card(request, card_id):
    card = get_object_or_404(Card, pk=card_id)

    could_be_in = _deck_count_at_least_color(
        card.identity_w,
        card.identity_u,
        card.identity_b,
        card.identity_r,
        card.identity_g
    )

    is_in = (
        Deck.objects
        .filter(card_list__card=card)
    )

    commands = (
        Deck.objects
        .filter(card_list__card=card, card_list__is_pdh_commander=True)
    )

    cmdrs = (
        CardInDeck.objects
        .filter(
            is_pdh_commander=True,
            deck__in=(
                Deck.objects
                .filter(card_list__card=card)
                .distinct()
            ),
        )
        .exclude(is_pdh_commander=True, card=card)
        .values('card')
        .annotate(count=Count('deck'))
        .values('count', 'card__id', 'card__name')
        .order_by('-count')
    )
    paginator = Paginator(cmdrs, 25, orphans=3)
    page_number = request.GET.get('page')
    cmdrs_page = paginator.get_page(page_number)

    return render(
        request,
        "single_card.html",
        context={
            'card': card,
            'is_in': is_in.count(),
            'commands': commands.count(),
            'could_be_in': could_be_in,
            'commanders': cmdrs_page,
            'links': _LINKS,
        },
    )


def single_cmdr(request, card_id):
    card = get_object_or_404(Card, pk=card_id)

    could_be_in = _deck_count_at_least_color(
        card.identity_w,
        card.identity_u,
        card.identity_b,
        card.identity_r,
        card.identity_g
    )

    commands = (
        Deck.objects
        .filter(card_list__card=card, card_list__is_pdh_commander=True)
    )

    common_cards = (
        CardInDeck.objects
        .filter(
            is_pdh_commander=False,
            deck__in=(
                Deck.objects
                .filter(card_list__card=card)
                .distinct()
            ),
        )
        .exclude(card__type_line__contains='Basic')
        .values('card')
        .annotate(count=Count('deck'))
        .values('count', 'card__id', 'card__name', 'card__type_line')
        .order_by('-count')
    )
    paginator = Paginator(common_cards, 25, orphans=3)
    page_number = request.GET.get('page')
    cards_page = paginator.get_page(page_number)

    return render(
        request,
        "single_cmdr.html",
        context={
            'card': card,
            'commands': commands.count(),
            'could_be_in': could_be_in,
            'common_cards': cards_page,
            'links': _LINKS,
        },
    )
