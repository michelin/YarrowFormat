import click

from ..yarrow import YarrowDataset_pydantic


def open(file_path=None, json_str=None) -> YarrowDataset_pydantic:
    if file_path:
        try:
            yar = YarrowDataset_pydantic.parse_file(file_path)
        except Exception as e:
            click.echo("File was not parsed correctly")
            click.echo(e)
            exit(101)
        click.echo("File was successfully parsed")
    elif json_str:
        try:
            yar = YarrowDataset_pydantic.parse_raw(json_str)
        except Exception as e:
            click.echo("Text was not parsed correctly")
            click.echo(e)
            exit(102)
        click.echo("JSON text was successfully parsed")
    else:
        click.echo("No valid input was given")
        exit(103)

    return yar
