import click
from hs_markov import cli

def test_main() -> None:
    runner = click.testing.CliRunner()
    result = runner.invoke(cli.main)

    assert result.exit_code == 0
