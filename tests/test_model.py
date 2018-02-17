import typing
import pytest
from hs_deckgen import model
from hs_deckgen import hearthstone
import numpy as np


class MockHearthstoneAPI:

    _CARDS = {
        0: hearthstone.Card(
            db_id=0,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 1',
        ),
        1: hearthstone.Card(
            db_id=1,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 2',
        ),
        2: hearthstone.Card(
            db_id=2,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 3',
        ),
        3: hearthstone.Card(
            db_id=3,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 4',
        ),
        4: hearthstone.Card(
            db_id=4,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 5',
        ),
        5: hearthstone.Card(
            db_id=5,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 6',
        ),
        6: hearthstone.Card(
            db_id=6,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 7',
        ),
        7: hearthstone.Card(
            db_id=7,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 8',
        ),
        8: hearthstone.Card(
            db_id=8,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 9',
        ),
        9: hearthstone.Card(
            db_id=9,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 10',
        ),
    }

    @classmethod
    def card_from_id(cls, card_id: int) -> typing.Optional[hearthstone.Card]:
        return cls._CARDS.get(card_id)

    @classmethod
    def all_cards(cls) -> typing.Set[hearthstone.Card]:
        return cls._CARDS.values()


@pytest.fixture
def deck_one() -> hearthstone.Deck:
    return hearthstone.Deck.from_cards([
        hearthstone.Card(
            db_id=0,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 1',
        ),
        hearthstone.Card(
            db_id=1,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 2',
        ),
        hearthstone.Card(
            db_id=2,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 3',
        )]
    )


@pytest.fixture
def deck_two() -> hearthstone.Deck:
    return hearthstone.Deck.from_cards([
        hearthstone.Card(
            db_id=1,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 2',
        ),
        hearthstone.Card(
            db_id=2,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 3',
        ),
        hearthstone.Card(
            db_id=3,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 4',
        )]
    )

def test_model(monkeypatch, deck_one, deck_two):
    monkeypatch.setattr(hearthstone, 'HearthstoneAPI', MockHearthstoneAPI)

    mod = model.HSModel.from_decks([deck_one, deck_two])
    assert sorted(mod.generate_deck(
        [hearthstone.Card(
            db_id=0,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 1',
        )],
        hearthstone.HSClass.MAGE,
        3,
    ).cards) == sorted(deck_one.cards)

    assert sorted(mod.generate_deck(
        [hearthstone.Card(
            db_id=3,
            hs_class=hearthstone.HSClass.MAGE,
            rarity=hearthstone.Rarity.COMMON,
            name='Card 4',
        )],
        hearthstone.HSClass.MAGE,
        3,
    ).cards) == sorted(deck_two.cards)
