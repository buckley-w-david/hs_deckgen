import click

@click.group()
def main() -> None:
    pass

@main.command()
@click.option('--partial', type=click.Path(exists=True))
def gendeck(partial: str) -> None:
    pass

@main.command()
@click.option('--outfile', type=click.Path(exists=False), required=True)
def genmodel() -> None:
    pass

#body/div[@id = "deck-info"]/@data-deck-cards
