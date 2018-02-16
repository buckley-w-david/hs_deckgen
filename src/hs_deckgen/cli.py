from contextlib import contextmanager
import json
import typing
import sys
import click
from hs_deckgen import deck as hs_deck
from hs_deckgen import model as hs_model


@contextmanager
def io_or_std(path: typing.Optional[str], mode: str = 'r') -> typing.IO:
    if path:
        with open(path, mode) as stream:
            yield stream
    else:
        if mode == 'r':
            yield sys.stdin
        elif mode =='w':
            yield sys.stdout
        elif mode == 'wb':
            yield sys.stdout.buffer
        elif mode == 'rb':
            yield sys.stdin.buffer

@click.group()
def main() -> None:
    pass

@main.command()
@click.option('--model', type=click.Path(exists=True), required=True)
@click.option('--partial', type=click.Path(exists=True))
@click.option('--output', type=click.Path(), required=False)
def deck(model: str, partial: str, output: str) -> None:
    with io_or_std(model, 'rb') as model_in, io_or_std(partial, 'r') as partial_in, io_or_std(output, 'w') as out:
        partial = [hs_deck.Card(card_id) for card_id in json.load(partial_in)]
        mod = hs_model.HSModel.load(model_in)
        deck = mod.generate_deck(partial)
        deck.save(out)


@main.command()
@click.option('--outfile', type=click.Path(exists=False), required=False)
@click.option('--train', type=click.Path(exists=True), required=False)
@click.option('--notrain', nargs=0, required=False)
def model(outfile, train, notrain) -> None:
    if not notrain:
        with io_or_std(train, 'r') as fin, io_or_std(outfile, 'wb') as fout:
            deck_locations = json.load(fin)
            decks = [hs_deck.Deck.from_hsreplay(deck_url) for deck_url in deck_locations]
            mod = hs_model.HSModel.from_decks(decks)
            mod.save(fout)
    else:
        with io_or_std(outfile, 'wb') as fout:
            mod = hs_model.HSModel()
            mod.save(fout)
