import datetime
from pathlib import Path
from typing import Generator, Union

import dateutil.parser
from sqlite_utils.db import Database
from warcio.archiveiterator import ArchiveIterator
from warcio.recordloader import ArcWarcRecord


class WARCDB(Database):
    """
    A container class for the underlying sqlite_utils.Database, which provides a
    way to add warc files, and fetch request and resonse records from the
    database.
    """

    def __init__(self, db_file: Union[str, None] = "warc.db") -> None:
        """
        Pass in the path to a SQLite database you would like to use or it will
        default to "warc.db" in the current working directory. If you would like
        to use an in memory SQLite database set db_file to None.
        """
        if db_file is not None:
            self.db: Database = Database(db_file)
        else:
            self.db: Database = Database(memory=True)

    def add_warc(self, warc_file: str) -> None:
        """
        Add a WARC file to the database.
        """
        files = self.db["files"]
        warc_file = Path(warc_file)
        files.insert(
            {
                "filename": warc_file.name,
                "path": str(warc_file.absolute()),
                "created": datetime.datetime.now(),
            },
            pk="id",
            columns={"created": datetime.datetime},
        )

        records = self.db["records"]
        count = 0
        with open(warc_file, "rb") as stream:
            rec_iterator = ArchiveIterator(stream)
            for rec in rec_iterator:
                count += 1
                records.insert(
                    _record_dict(rec, files.last_pk, rec_iterator),
                    pk="id",
                    columns={
                        "warc_content_length": int,
                        "warc_segment_total_length": int,
                        "warcio_offset": int,
                        "warcio_length": int,
                        "warc_date": datetime.datetime,
                        "http_date": datetime.datetime,
                        "http_payload": "blob",
                        "warc_refers_to_date": datetime.datetime,
                    },
                )

        return count

    @property
    def files(self) -> Generator:
        """
        Return a generator for all the WARC files that have been added to the
        database.
        """
        return self.db["files"].rows

    @property
    def requests(self) -> Generator:
        """
        Return a generator for all the request records present in the database.
        """
        return self.db["records"].rows_where('warc_type = "request"')

    @property
    def responses(self) -> Generator:
        """
        Return a generator for all the response records in the database.
        """
        return self.db["records"].rows_where('warc_type = "response"')


def _record_dict(
    rec: ArcWarcRecord, file_id: int, rec_iterator: ArchiveIterator
) -> dict:
    """
    Turn a WARC record into a dictionary suitable for inserting into the records
    table.
    """
    warc_header = rec.rec_headers.get_header

    if rec.http_headers is not None:
        http_header = rec.http_headers.get_header
        http_headers = dict(rec.http_headers.headers)
        http_status = rec.http_headers.get_statuscode()
    else:
        http_header = {}.get
        http_headers = None
        http_status = None

    return {
        "file_id": file_id,
        # WARC headers
        "warc_record_id": warc_header("WARC-Record-ID"),
        "warc_type": warc_header("WARC-Type"),
        "warc_content_length": int(warc_header("Content-Length", 0)),
        "warc_date": parse_date(warc_header("WARC-Date")),
        "warc_concurrent_to": warc_header("WARC-Concurrent-To"),
        "warc_block_digest": warc_header("WARC-Block-Digest"),
        "warc_payload_digest": warc_header("WARC-Payload-Digest"),
        "warc_ip_address": warc_header("WARC-IP-Address"),
        "warc_refers_to": warc_header("WARC-Refers-To"),
        "warc_refers_to_target_uri": warc_header("WARC-Refers-To-Target-URI"),
        "warc_refers_to_date": parse_date(warc_header("WARC-Refers-To-Date")),
        "warc_target_uri": warc_header("WARC-Target-URI"),
        "warc_truncated": warc_header("WARC-Truncated"),
        "warc_warcinfo_id": warc_header("WARC-Warcinfo-ID"),
        "warc_filename": warc_header("WARC-Filename"),
        "warc_profile": warc_header("WARC-Profile"),
        "warc_identified_payload_type": warc_header("WARC-Identified-Payload-Type"),
        "warc_segment_number": warc_header("WARC-Segment-Number"),
        "warc_segment_origin_id": warc_header("WARC-Segment-Origin-ID"),
        "warc_segment_total_length": warc_header("WARC-Segment-Total-Length"),
        # HTTP headers
        "http_status": http_status,
        "http_content_type": http_header("Content-Type"),
        "http_server": http_header("Server"),
        "http_date": parse_date(http_header("Date")),
        "http_content_length": http_header("Content-Length"),
        "http_headers": http_headers,
        "http_payload": rec.content_stream().read(),
        # Things from warcio
        "warcio_offset": rec_iterator.get_record_offset(),
        "warcio_length": rec_iterator.get_record_length(),
    }


def parse_date(s: str) -> Union[None, datetime.datetime]:
    if s is None:
        return None
    else:
        return dateutil.parser.parse(s)
