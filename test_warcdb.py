from pathlib import Path

from pytest import fixture

from warcdb import WARCDB


@fixture
def test_db() -> WARCDB:
    db = WARCDB(db_file=None)
    db.add_warc("test-data/apod.warc.gz")
    return db


def test_files(test_db: WARCDB) -> None:
    assert len(list(test_db.files)) == 1
    file = next(test_db.files)
    assert file["filename"] == "apod.warc.gz"
    assert file["path"] == str(Path.cwd() / "test-data" / "apod.warc.gz")


def test_add(test_db: WARCDB) -> None:
    assert test_db.db["records"].count == 807, "expected number of records in db"
    assert test_db.db["files"].count == 1, "expected number of files in db"
    for record in test_db.db["records"].rows:
        assert record["file_id"] == 1


def test_requests(test_db: WARCDB) -> None:
    request = next(test_db.requests)
    assert request, "found a request record"
    assert request["id"] == 2, "primary key is set"
    assert request["warc_date"] == "2022-05-10T01:03:24+00:00", "warc_date normalized"


def test_responses(test_db: WARCDB) -> None:
    assert len(list(test_db.responses)) == 402
    response = next(test_db.responses)
    assert response, "found a response record"
    assert response["id"] == 1, "primary key is set"
    assert response["warc_date"] == "2022-05-10T01:03:24+00:00"
    assert response["http_date"] == "2022-05-10T01:03:24+00:00"
