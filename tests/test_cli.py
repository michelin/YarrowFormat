import re

import pytest
from click.testing import CliRunner

from yarrow import cli


@pytest.fixture
def cli_runner():
    return CliRunner()


def test_exit_codes(cli_runner: CliRunner):

    result = cli_runner.invoke(cli, ["--help"])
    assert result.exit_code == 0

    result = cli_runner.invoke(cli)
    assert result.exit_code == 0

    result = cli_runner.invoke(cli, [""])
    assert result.exit_code == 2

    result = cli_runner.invoke(cli, ["123"])
    assert result.exit_code == 2

    result = cli_runner.invoke(cli, [456])
    assert result.exit_code == 1


def test_check_invoke(cli_runner: CliRunner):
    result = cli_runner.invoke(cli, ["check"])
    assert result.exit_code == 103

    result = cli_runner.invoke(cli, ["check", "--help"])
    assert result.exit_code == 0

    result = cli_runner.invoke(
        cli,
        [
            "check",
            "--json",
            "-f",
            "examples/generate_simple/example_simple.yarrow.json",
        ],
    )
    pattern = re.compile("File was successfully parsed.*")
    assert re.match(pattern, result.output)
