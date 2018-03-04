import io
import itertools
import pickle
import typing
import numpy as np
import requests

from hearthstone import hsdata
from hearthstone import deck
from hearthstone import card
from hearthstone import api


L = typing.TypeVar('L')
R = typing.TypeVar('R')
class BijectiveMap():

    def __init__(self, tuples: typing.Optional[typing.List[typing.Tuple[L, R]]] = None) -> None:
        self._left: typing.Dict[L, R] = {}
        self._right: typing.Dict[R, L] = {}

        if tuples:
            for l, r in tuples:
                self._left[l] = r
                self._right[r] = l

    def __setitem__(self, left: L, right: R) -> None:
        self._left[left] = right
        self._right[right] = left

    def __len__(self) -> int:
        return len(self._left)

    @property
    def left(self) -> typing.Dict[L, R]:
        return self._left

    @property
    def right(self) -> typing.Dict[R, L]:
        return self._right


class HSModel:

    def __init__(self):
        cards = api.HearthstoneAPI.all_cards()

        self._class_indexs = {hsdata.HSClass.NEUTRAL: []}
        self._map = _map = BijectiveMap()
        count = 0

        for i, card in enumerate(cards):
            for idx in range(1 + (card.rarity is not hsdata.Rarity.LEGENDARY)):
                self._class_indexs.setdefault(card.hs_class, []).append(count)
                _map[(card.db_id, idx)] = count
                count += 1

        self._model = np.zeros([count, count])
        self._norm = np.ones([count])


    def _deck_to_rows(self, deck: typing.List[card.Card]) -> typing.List[int]:
        keyfunc = lambda card: card.db_id
        cards = sorted(deck, key=keyfunc)
        return [self._map.left[(sub_db_id, sub_count)]
                for sub_db_id, sub_group in itertools.groupby(cards, key=keyfunc)
                for sub_count, _ in enumerate(sub_group)]

    def train(self, deck: typing.List[card.Card]):
        rows = np.array(self._deck_to_rows(deck))
        self._model[rows[:, None], rows] += len(rows)
        self._norm[rows] += len(rows)

    #TODO - Other constraints (mana, stats, etc)
    #FIXME - Normalization still not right
    def generate_deck(self, partial: typing.List[card.Card], hs_class: hsdata.HSClass, deck_size=30):
        assert len(partial) >= 0
        assert len(partial) <= deck_size

        class_indexs = self._class_indexs.copy()
        class_indexs.pop(hs_class)
        class_indexs.pop(hsdata.HSClass.NEUTRAL)

        model = self._model / self._norm
        for indexs in class_indexs.values():
            model[:,indexs] = -1
        np.fill_diagonal(model, -1)

        generated_deck = []
        generated_deck.extend(partial)

        # import pdb; pdb.set_trace()
        model[:, self._deck_to_rows(generated_deck)] = -1
        chosen = set()

        for _ in range(deck_size - len(generated_deck)):
            rows = self._deck_to_rows(generated_deck)
            combined = np.sum(model[rows], axis=0)
            index = np.random.choice(np.argwhere(combined == np.max(combined)).ravel())
            card_id, n = self._map.right[index]

            if n and index-1 not in chosen:
                model[:,index-1] = -1
                chosen.add(index-1)
            else:
                model[:,index] = -1
                chosen.add(index)

            card = api.HearthstoneAPI.card_from_id(card_id)

            generated_deck.append(card)


        return deck.Deck(generated_deck, hs_class)

    @classmethod
    def from_decks(cls, decks: typing.Iterable[deck.Deck]) -> 'HSModel':
        model = HSModel()
        for deck in decks:
            model.train(deck)

        return model

    @classmethod
    def load(cls, stream: typing.IO[bytes]) -> 'HSModel':
        return pickle.load(stream)

    def save(self, stream: typing.IO[bytes]) -> None:
        pickle.dump(self, stream)
