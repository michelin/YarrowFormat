"""CLI value validity functions. Experimental
"""
import click

from ..yarrow import YarrowDataset_pydantic
from .open import open_yarrow


def check_default(yar: YarrowDataset_pydantic):
    end_res, results = yar._check_valid_ids()

    return {"result": end_res, "detail": results}


pattern_available = {"default": check_default}


@click.command(name="check", help="Performs basic Yarrow parsing check")
@click.option(
    "--json/--no-json", "json_opt", default=False, help="Will output in json format"
)
@click.option("-f", "--file-path", default=None, help="Yarrow file to check")
@click.option(
    "-j", "--json-input", "json_str", default=None, help="Yarrow JSON text to check"
)
@click.option(
    "--pattern",
    type=click.Choice(["default"]),
    multiple=True,
    help="Pattern(s) to check",
    show_choices=True,
)
def check(file_path=None, json_str=None, json_opt=False, pattern=None):

    yar = open_yarrow(file_path, json_str)

    if json_opt:
        click.echo({"result": True, "yarrow": yar.json(exclude_unset=True)})

    if pattern and isinstance(pattern, tuple):
        for pat in pattern:
            if pat in pattern_available.keys():
                click.echo(pattern_available[pat](yar))

    return True
