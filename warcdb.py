from sqlite_utils.db import Database
from warcio.archiveiterator import ArchiveIterator


def from_warc(warc_input, db_file=None) -> Database:
    """
    Read in WARC data and return a SQLite database for it.
    """
    if db_file:
        db = Database('test.db')
    else:
        db = Database(memory=True)

    load_warc(db, warc_input)

    return db


def load_warc(db, warc_input) -> Database:
    """
    Load a sqlite_utils Database with WARC data.
    """
    records = db['records']
    with open(warc_input, 'rb') as stream:
        for warc_record in ArchiveIterator(stream):
            if warc_record.rec_type == 'response':
                records.insert(response_record(warc_record))

    return db


def response_record(warc_record) -> dict:
    """
    Extract information from a WARC Response Record into a dictionary.
    """
    header = warc_record.rec_headers.get_header
    return {
        "warc_record_id": header("WARC-Record-ID"),
        "warc_twarget_uri": header("WARC-Target-URI"),
    }
