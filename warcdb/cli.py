from typing import List

import click

import warcdb


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("warc_files", nargs=-1)
def add(warc_files: List[str], type: str = click.Path(exists=True)) -> None:
    """Add one or more WARC files to the database."""
    db = warcdb.WARCDB()
    for warc_file in warc_files:
        records = db.add_warc(warc_file)
        click.echo(f"imported {records} records from {warc_file}")


@cli.command()
def list() -> None:
    """List all the files that have been imported into the database."""
    db = warcdb.WARCDB()
    for file in db.files:
        click.echo(f"{file['created']}  {file['filename']}")
