import typing
from hearthstone import hsdata


class _Card(typing.NamedTuple):
    db_id: int
    hs_class: hsdata.HSClass
    rarity: hsdata.Rarity
    name: str


class Card(_Card):

    @classmethod
    def from_id(cls, db_id: int) -> 'Card':
        raise NotImplementedError()

    @classmethod
    def from_json(cls, json: typing.Dict[str, typing.Any]) -> 'Card':
        return Card(
            db_id=json['db_id'],
            hs_class=getattr(hsdata.HSClass, json['hs_class']),
            rarity=getattr(hsdata.Rarity, json['rarity']),
            name=json['name'],
        )

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {
            'db_id': self.db_id,
            'hs_class': self.hs_class.name,
            'rarity': self.rarity.name,
            'name': self.name,
        }
