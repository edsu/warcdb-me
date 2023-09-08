import warcdb

def test_sqlite():
    db = warcdb.sqlite_from_warc('test-data/apod.warc.gz')
    assert db.execute("SELECT COUNT(*) FROM records").fetchone()[0] == 402

def test_pandas():
    df = warcdb.pandas_from_warc('test-data/apod.warc.gz')
    assert len(df) == 402
