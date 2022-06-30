"""CLI save module
"""
import sys

import click

from .open import open_yarrow


@click.command("save", help="Save the given content at the specified path")
@click.option("-f", "--file-path", default=None, help="Yarrow file to check")
@click.option(
    "-j", "--json-input", "json_str", default=None, help="Yarrow JSON text to check"
)
@click.option(
    "--output", "output_path", default=None, help="File path to save the file"
)
def save(file_path: str = None, json_str: str = None, output_path: str = None) -> None:
    """Save the given content, file or string, to the given output path

    :param file_path: Input file path, defaults to None
    :type file_path: str, optional
    :param json_str: JSON string which must be parsed, defaults to None
    :type json_str: str, optional
    :param output_path: Ouput path to save the file, defaults to None
    :type output_path: str, optional
    :return: Return True on completion or exits with error code 104 if no
            output_path was given or exits with error code 105 if the file
            could not be saved
    :rtype: bool
    """

    yar = open_yarrow(file_path=file_path, json_str=json_str)

    if output_path:
        try:
            yar.save_to_file(output_path)
        except Exception as e:
            click.echo("Could not save file")
            click.echo(e)
            sys.exit(105)
    else:
        click.echo("No path specified")
        sys.exit(104)

    return True
