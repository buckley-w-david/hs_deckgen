import io
import pickle
import typing
import numpy as np
import requests
from hs_deckgen import hearthstone


class HSModel:

    def __init__(self):
        cards = hearthstone.HearthstoneAPI.all_cards()

        self._class_indexs = {getattr(hearthstone.HSClass, hs_class): [] for hs_class in hearthstone.HSClass.__members__.keys()}
        self._db_to_id = {}
        self._id_to_card ={}

        for i, card in enumerate(cards):
            self._class_indexs[card.hs_class].append(i)

            self._db_to_id[card.db_id] = i
            self._id_to_card[i] = card.db_id

        m = len(cards)

        self._model = np.zeros([m, m])
        self._norm = np.ones([m, 1])


    def _db_to_model_index(self, db_id: int) -> typing.Optional[int]:
        return self._db_to_id.get(db_id)

    def _model_index_to_card(self, index: int) -> typing.Optional[hearthstone.Card]:
        return hearthstone.HearthstoneAPI.card_from_id(self._id_to_card.get(index))

    #TODO - Other constraints (mana, stats, etc)
    #FIXME - Normalization too harsh?
    def generate_deck(self, partial: typing.List[hearthstone.Card], hs_class: hearthstone.HSClass):
        assert len(partial) > 0
        assert len(partial) <= 30

        import pdb; pdb.set_trace()

        class_indexs = self._class_indexs.copy()
        class_indexs.pop(hs_class)
        class_indexs.pop(hearthstone.HSClass.NEUTRAL)

        model = self._model / self._norm
        # import pdb;pdb.set_trace()
        for indexs in class_indexs.values():
            model[:,indexs] = -1

        generated_deck = []
        generated_deck.extend(partial)

        for _ in range(30 - len(generated_deck)):
            combined = np.sum(model[[self._db_to_model_index(card.db_id) for card in generated_deck]], axis=0)

            index = np.random.choice(np.argwhere(combined == np.max(combined)).ravel())

            card = self._model_index_to_card(index)

            if card in generated_deck or card.rarity is hearthstone.Rarity.LEGENDARY:
                model[:,index] = -1

            generated_deck.append(card)

        return hearthstone.Deck(generated_deck, hs_class)

    def save(self, stream: typing.IO[bytes]) -> None:
        pickle.dump(self, stream)

    def train(self, deck):
        unique = deck.unique
        doubles = deck.doubles

        for card in unique:
            row_idx = self._db_to_model_index(card.db_id)
            self._model[row_idx, [self._db_to_model_index(sub_card.db_id) for sub_card in (unique - {card})]] += 1
            self._model[row_idx, row_idx] += (card in doubles)
            self._norm[row_idx][0] += 1

    @classmethod
    def from_decks(cls, decks: typing.Iterable[hearthstone.Deck]) -> 'HSModel':
        model = HSModel()
        for deck in decks:
            model.train(deck)

        return model

    @classmethod
    def load(cls, stream: typing.IO[bytes]) -> 'HSModel':
        return pickle.load(stream)
