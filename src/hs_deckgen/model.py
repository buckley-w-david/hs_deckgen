import io
import pickle
import typing
import numpy as np
import requests
from hs_deckgen import deck


class HSModel:

    def __init__(self):
        endpoint = 'https://api.hearthstonejson.com/v1/latest/enUS/cards.collectible.json'
        with requests.get(endpoint) as r:
            cards = r.json()

        self._db_to_id = {}
        self._id_to_db ={}
        for i, card in enumerate(cards):
            self._db_to_id[card['dbfId']] = i
            self._id_to_db[i] = card['dbfId']

        m = len(cards)

        self._model = np.zeros([m, m])
        self._norm = np.ones([m, 1])

    #TODO - Class constraints
    #TODO - Legendary count constraint
    #TODO - Other constraints (mana, stats, etc)
    #FIXME - Normalization too harsh?
    def generate_deck(self, partial: typing.List[deck.Card]):
        assert len(partial) > 0
        assert len(partial) <= 30

        model = self._model / self._norm
        generated_deck = []
        generated_deck.extend(partial)

        for _ in range(30 - len(generated_deck)):
            combined = np.sum(model[[self._db_to_id.get(card.db_id) for card in generated_deck]], axis=0)

            index = np.random.choice(np.argwhere(combined == np.max(combined)).ravel())

            id_to_add = self._id_to_db.get(index)
            card = deck.Card(db_id=id_to_add)

            if card in generated_deck:
                model[:,index] = -1

            generated_deck.append(card)

        # import pdb; pdb.set_trace()
        return deck.Deck(generated_deck)

    def save(self, stream: typing.IO[bytes]) -> None:
        pickle.dump(self, stream)

    def train(self, deck):
        for card in deck.unique:
            row_idx = self._db_to_id.get(card.db_id)
            self._model[row_idx, [self._db_to_id.get(sub_card.db_id) for sub_card in (deck.unique - {card})]] += 1
            self._model[row_idx, row_idx] += (card in deck.doubles)
            self._norm[row_idx][0] += 1

    @classmethod
    def from_decks(cls, decks: typing.List[deck.Deck]) -> 'HSModel':
        model = HSModel()
        for deck in decks:
            model.train(deck)

        return model

    @classmethod
    def load(cls, stream: typing.IO[bytes]) -> 'HSModel':
        return pickle.load(stream)
