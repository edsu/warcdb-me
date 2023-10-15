from typing import List

import click

import warcdb


@click.group()
@click.pass_context
@click.option("--db", default="warc.db", help="A path to a SQLite database to use")
def cli(ctx: dict, db: str) -> None:
    ctx.ensure_object(dict)
    ctx.obj['db'] = db


@cli.command()
@click.pass_context
@click.argument("warc_files", nargs=-1)
def add(ctx: dict, warc_files: List[str], type: str = click.Path(exists=True)) -> None:
    """Add one or more WARC files to the database."""
    db = warcdb.WARCDB(ctx.obj['db'])
    for warc_file in warc_files:
        records = db.add_warc(warc_file)
        click.echo(f"imported {records} records from {warc_file}")


@cli.command()
@click.pass_context
def list(ctx: dict) -> None:
    """List all the files that have been imported into the database."""
    db = warcdb.WARCDB(ctx.obj['db'])
    for file in db.files:
        click.echo(f"{file['created']}  {file['filename']}")
