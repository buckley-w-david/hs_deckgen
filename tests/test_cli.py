from click.testing import CliRunner
from hs_markov import cli

def test_main() -> None:
    runner = CliRunner()
    result = runner.invoke(cli.main)

    assert result.exit_code == 0
