# warcdb

[![Build Status](https://github.com/edsu/warcdb/actions/workflows/test.yml/badge.svg)](https://github.com/edsu/warcdb/actions/workflows/test.yml)

The [WARC] file format is used extensively in web archiving software, but most people aren't familiar with working with it directly because crawling and replay tools tend to hide the nitty gritty details of how to use it. This can make it somewhat difficult to use WARC data directly in analysis and research where you want to query and interact with the collected web archive data. *warcdb* tries to make analyzing WARC data easier by allowing you to import it into an [SQLite] database, and then letting you use SQL and other SQLite tools like [Datasette] to analyze the WARC data.

## Install

```bash
$ pip install warcdb
```

## Command Line Usage

Once installed you should have a *warcdb* utility available on the command line. *warcdb* takes a few subcommands that let you interact with the database.

### add

Create a warcdb database with the default name `warc.db` in the current working directory using two WARC files:

```bash
$ warcdb add warc1.warc.gz warc2.warc.gz
```

Create a warcdb database with a specific name and location:

```bash
$ warcdb --db /path/to/my/warcdb/archive.sqlite3 add warc1.warc.gz
```

Adding another WARC file to the existing database can be achieved using the same `add` command:

```bash
$ warcdb add warc3.warc.gz
```

### list

List the WARC files that have been added to a database (looking in the current working directory for `warc.db`:

```bash
$ warcdb list
```

Or listing the WARC files in a specific database:

```bash
$ warcdb --db /path/to/my/warcdb/archive.sqlite3 list
```

## The Database

You can use any tools that can interact with SQLite to query the data. For
example you can use the `sqlite3` command line tool print out the database
schema:

```bash
$ sqlite3 warc.db
```

### Schema

```sqlite
sqlite> .schema
CREATE TABLE [files] (
   [id] INTEGER PRIMARY KEY,
   [filename] TEXT,
   [created] TEXT
);
CREATE TABLE [records] (
   [id] INTEGER PRIMARY KEY,
   [file_id] INTEGER,
   [warc_record_id] TEXT,
   [warc_type] TEXT,
   [warc_content_length] INTEGER,
   [warc_date] TEXT,
   [warc_concurrent_to] TEXT,
   [warc_block_digest] TEXT,
   [warc_payload_digest] TEXT,
   [warc_ip_address] TEXT,
   [warc_refers_to] TEXT,
   [warc_refers_to_target_uri] TEXT,
   [warc_refers_to_date] TEXT,
   [warc_target_uri] TEXT,
   [warc_truncated] TEXT,
   [warc_warcinfo_id] TEXT,
   [warc_filename] TEXT,
   [warc_profile] TEXT,
   [warc_identified_payload_type] TEXT,
   [warc_segment_number] TEXT,
   [warc_segment_origin_id] TEXT,
   [warc_segment_total_length] INTEGER,
   [http_status] TEXT,
   [http_content_type] TEXT,
   [http_server] TEXT,
   [http_date] TEXT,
   [http_content_length] TEXT,
   [http_headers] TEXT,
   [http_payload] BLOB,
   [warcio_offset] INTEGER,
   [warcio_length] INTEGER
);
```

All the WARC records are stored in the same table, but not all the columns will be populated depending on the `warc_type` which corresponds to the records `WARC-Type`: request, response, info, etc. See the [WARC Specification] for details.

Most of the columns in the `records` table come directly from the [WARC Specification], however some HTTP headers have also been extracted to help in using the data, these are prefixed with `http_`. This also includes the payload of the HTTP response. The `warcio_offset` and `warcio_length` columns contain integers that reference where in the original WARC data the record can be found.

### Queries

For example you could run a SQL query to see what the most popular `Content-Type` values in server responses there are in the database:

```
sqlite> SELECT http_content_type, COUNT(*) AS total
   ...> FROM records
   ...> WHERE warc_type = 'response'
   ...> GROUP BY http_content_type
   ...> ORDER BY total DESC;
   
http_content_type                         total
----------------------------------------  -----
text/html; charset=UTF-8                  116
image/jpeg                                99
image/gif                                 92
application/json; charset=UTF-8           16
text/javascript                           14
application/json; charset=utf-8           11
application/json+protobuf; charset=UTF-8  10
application/octet-stream                  7
video/mp4                                 5
image/webp                                5
application/javascript                    5
                                          5
text/html; charset=iso-8859-1             4
text/plain                                3
text/html; charset=utf-8                  3
application/x-chrome-extension            3
text/css                                  1
image/x-icon                              1
font/woff2                                1
application/rss+xml                       1
```

### HTTP Headers

The `http_headers` column contains a JSON object that has all the headers sent or received in requests and responses respectively. You can use [SQLite's JSON functions] to select out headers of interest. For example if you wanted to inspect the `Last-Modified` headers that were sent in responses from a server:

```sqlite
sqlite> SELECT http_headers -> '$.last-modified' AS last_modified
   ...> FROM records
   ...> WHERE warc_type = 'response' AND last_modified IS NOT NULL; 
   
last_modified
-------------------------------
"Wed, 17 Jul 2019 00:41:02 GMT"
"Wed, 10 Oct 2018 17:49:21 GMT"
"Mon, 11 Apr 2022 19:43:09 GMT"
"Thu, 07 Apr 2022 20:36:58 GMT"
"Thu, 05 May 2022 18:50:23 GMT"
"Tue, 28 Jul 2020 19:50:19 GMT"
"Mon, 28 Mar 2022 17:23:50 GMT"
"Mon, 29 Mar 2021 22:42:38 GMT"
"Wed, 20 Apr 2022 22:39:05 GMT"
"Wed, 23 Mar 2022 16:40:40 GMT"
"Tue, 14 May 2019 19:41:29 GMT"
"Fri, 24 Jun 2022 20:44:18 GMT"
"Tue, 14 May 2019 19:41:29 GMT"
"Fri, 24 Jun 2022 20:44:18 GMT"
"Wed, 13 Apr 2022 21:02:38 GMT"
"Sun, 17 May 1998 03:00:00 GMT"
"Tue, 14 May 2019 19:41:29 GMT"
"Fri, 24 Jun 2022 20:44:18 GMT"
```

## Datasette

One useful way of exploring the database is to view it with [datasette] with some additional plugins enabled for viewing JSON and images.

```
$ pip install datasette datasette-render-images datasette-pretty-json
$ datasette warc.db
```

[WARC Specification]: https://iipc.github.io/warc-specifications/specifications/warc-format/warc-1.1/
[SQLite's JSON functions]: https://www.sqlite.org/json1.html
[Datasette]: https://datasette.io/
[SQLite]: https://www.sqlite.org/index.html
[WARC]: https://en.wikipedia.org/wiki/WARC_(file_format)
