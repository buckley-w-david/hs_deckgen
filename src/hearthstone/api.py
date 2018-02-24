import enum
import itertools
import json
import typing
import urllib.request
import urllib.parse
from lxml import html, etree
import requests
import base64

from hearthstone import deck
from hearthstone import card
from hearthstone import hsdata


class ReplayAPI:

    # TODO - fix
    @classmethod
    def top_decks(cls, n=None) -> typing.Iterator[deck.Deck]:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' + \
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }

        base = 'https://hsreplay.net'
        url = urllib.parse.urljoin(base, 'decks')

        with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as request:
            document = html.parse(request)

        query = "body/div[@id = 'decks-container']/div[@class = 'deck-list-wrapper']/div[@class = 'deck-list']/ul/li/a/@href"
        if n:
            snipper = range(n)
        else:
            snipper = itertools.count()

        for _, href in zip(snipper, document.xpath(query)):
            url = urllib.parse.urljoin(base, href)
            yield deck.Deck.from_hsreplay(url)


class HearthstoneAPI:

    _CARDS = None

    @classmethod
    def _get_cards(cls) -> None:
        endpoint = 'https://api.hearthstonejson.com/v1/latest/enUS/cards.collectible.json'
        with requests.get(endpoint) as r:
            cards = r.json()

        cls._CARDS = {
            dict_card['dbfId']: card.Card(
                db_id=dict_card['dbfId'],
                hs_class=getattr(hsdata.HSClass, dict_card['playerClass']),
                rarity=getattr(hsdata.Rarity, dict_card['rarity']),
                name=dict_card['name'],
            ) for dict_card in cards
        }

    def lazy_cards(func):
        def decorated(*args, **kwargs):
            if HearthstoneAPI._CARDS is None:
                HearthstoneAPI._get_cards()
            return func(*args, **kwargs)
        return decorated

    @classmethod
    @lazy_cards
    def card_from_id(cls, card_id: int) -> typing.Optional[card.Card]:
        return cls._CARDS.get(card_id)


    @classmethod
    def deck_from_url(cls, url: str) -> deck.Deck:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' + \
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }

        with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as request:
            document = html.parse(request)

        deck_info = document.xpath("body/div[@id = 'deck-info']")[0]
        cards = [HearthstoneAPI.card_from_id(int(id)) for id in deck_info.attrib['data-deck-cards'].split(',')]

        hs_class = getattr(hsdata.HSClass, deck_info.attrib['data-deck-class'])

        return deck.Deck(cards, hs_class)


    @classmethod
    @lazy_cards
    def all_cards(cls) -> typing.Set[card.Card]:
        return cls._CARDS.values()
