from contextlib import contextmanager
import typing
import sys
import click
import json

from trainer import replay_trainer
from hearthstone import api


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
@click.option('--outfile', type=click.Path(exists=False), required=False)
@click.option('--input_cards', type=click.Path(exists=True), required=False)
@click.option('--pages', type=int, required=False)
def replay(outfile: typing.Optional[str], input_cards: typing.Optional[str], pages: typing.Optional[int]) -> None:
    if input_cards:
        with open(input_cards) as file:
            cards = map(api.HearthstoneAPI.card_from_id, json.load(file))

        with io_or_std(outfile, 'wb') as fout:
            mod = replay_trainer.ReplayTrainer.model_from_cards(cards)
            mod.save(fout)
    else:
        with io_or_std(outfile, 'wb') as fout:
            mod = replay_trainer.ReplayTrainer.new_model(pages)
            mod.save(fout)
