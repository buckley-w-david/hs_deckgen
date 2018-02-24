from contextlib import contextmanager
import json
import typing
import sys
import click
from hearthstone import deck
from hearthstone import card
from hearthstone import hsdata
from hearthstone import api

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
@click.option('--hsclass', type=str, required=False)
@click.option('--partial', type=click.Path(exists=True))
@click.option('--output', type=click.Path(), required=False)
def deck(model: str, hsclass: str, partial: str, output: str) -> None:

    with open(model, 'rb') as model_in, io_or_std(partial, 'r') as partial_in, io_or_std(output, 'w') as out:
        partial = [api.HearthstoneAPI.card_from_id(id) for id in json.load(partial_in)]
        if not hsclass:
            scan = filter(
                lambda hs_class: hs_class is not hsdata.HSClass.NEUTRAL,
                map(
                    lambda card: card.hs_class,
                    partial
                )
            )
            hs_class = next(scan)
        else:
            hs_class = getattr(hsdata.HSClass, hsclass)

        mod = hs_model.HSModel.load(model_in)
        deck = mod.generate_deck(partial, hs_class)
        deck.save(out)
        print()

@main.command()
@click.option('--outfile', type=click.Path(exists=False), required=False)
@click.option('--training', type=click.Path(exists=True), required=False)
@click.option('--train/--notrain', default=True)
def model(outfile, training, train) -> None:
    if train:
        with io_or_std(training, 'r') as fin, io_or_std(outfile, 'wb') as fout:
            deck_locations = json.load(fin)
            decks = (deck.Deck.from_hsreplay(deck_url) for deck_url in deck_locations)
            mod = hs_model.HSModel.from_decks(decks)
            mod.save(fout)
    else:
        with io_or_std(outfile, 'wb') as fout:
            mod = hs_model.HSModel()
            mod.save(fout)
