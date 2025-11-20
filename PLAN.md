# Plan

Deleting Codes from document

A minimally working piece of software will require the following features:

1. Loading data into Mise

Mise is oriented toward working with text data, and as a first pass on the software only text data functionality will be added. This requires all sorts of data formats that can be imported but I think most users will need to import docx and PDF files but I want to add support for doc and md formats as well

2. Annotating data with codes

Annotating data with codes is the bare minimum functionality that needs to be developed. Codes need to be able to be applied to chunks of text but the question becomes how to shape this feature to match the overarching principle of Mise which is that codes should be added to larger chunks of text. 

3. Getting reports out of Mise

Mise can only be a successful analysis tool if it is capable of generating summaries or the annotated data. In essence that is what a QDA software is. But the question becomes how should it be formatted. As a first pass I think that PDFs that display the chunked annotated tags is a good start. 

## Dev Notes

There are so many different pieces of the software that needs to be developed for these functionalities to actually work. The one that I think is most difficult is how codes are stored and associated with text. So these are two different structures the first stores codes and hopefully in a hierarchical way with two levels parent and child and the second is storing the relationship of codes to data.

Another question I have is how data should be managed: a user imports their data into Mise by storing it in the /data directory but what if they then code the data and then change the underlying data. I think that this necessitates storing the text data from the user into a new format and new directory hidden from the user. So that is they upload a file "transcript.docx" it gets quietly converted to plaintext and stored in a directory ".data" with the name "transcript.mise" with write permissions disabled.

```
my_project.mise/
    project.db         # SQLite, main metadata
    texts/
        doc_0001.txt   # normalized UTF-8 text
        doc_0002.txt
    meta/
        codebook.json  # optional export/import format
        config.json    # view prefs, etc.
```


For storing data we are going to use SQL with three core tables 

**Documents**

```SQL
CREATE TABLE documents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid            TEXT NOT NULL UNIQUE, -- stable ID if you export/import
    label           TEXT NOT NULL,        -- user-facing name
    original_name   TEXT NOT NULL,        -- e.g. "transcript.docx"
    original_path   TEXT,                 -- where it came from (optional)
    text_path       TEXT NOT NULL,        -- e.g. "texts/doc_0001.txt"
    mime_type       TEXT,                 -- e.g. "application/vnd.openxmlformats..."
    checksum        TEXT,                 -- hash of canonical text
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);
```

**Codes**

```SQL
CREATE TABLE codes (
    id          TEXT PRIMARY KEY,               -- e.g. "pain", or UUID
    label       TEXT NOT NULL,
    parent_id   TEXT REFERENCES codes(id),
    description TEXT,
    color       TEXT,
    sort_order  INTEGER
);
```

**Coded Segments**

```SQL
CREATE TABLE coded_segments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id     INTEGER NOT NULL REFERENCES documents(id),
    code_id         TEXT NOT NULL REFERENCES codes(id),
    start_offset    INTEGER NOT NULL,  -- char offset inclusive
    end_offset      INTEGER NOT NULL,  -- char offset exclusive
    memo            TEXT,
    created_at      TEXT NOT NULL,
    created_by      TEXT
);
```








# `todo`

- add PDF reading and conversion to `mise/utils/file_io.py` with function `read_pdf`