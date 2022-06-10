import click

from .open import open


@click.command("save", help="Save the given content at the specified path")
@click.option("-f", "--file-path", default=None, help="Yarrow file to check")
@click.option(
    "-j", "--json-input", "json_str", default=None, help="Yarrow JSON text to check"
)
@click.option(
    "--output", "output_path", default=None, help="File path to save the file"
)
def save(file_path=None, json_str=None, output_path=None):

    yar = open(file_path=file_path, json_str=json_str)

    if output_path:
        try:
            yar.save_to_file(output_path)
        except Exception as e:
            click.echo("Could not save file")
            click.echo(e)
    else:
        click.echo("No path specified")
        exit(104)

    return True
