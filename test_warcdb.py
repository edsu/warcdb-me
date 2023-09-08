import warcdb

def test_sqlite():
    db = warcdb.from_warc('test-data/apod.warc.gz')
    assert db.execute("SELECT COUNT(*) FROM records").fetchone()[0] == 402
