import click

from .cli import check, save


@click.group()
def cli():
    pass


cli.add_command(check)
cli.add_command(save)

if __name__ == "__main__":
    cli()
