# Mise Architecture Overview

## Goals
- Minimalist QDA tool: import text, code data, export coded segments, and reports

## Core Concepts
- Project = folder with SQLite DB + data directories
- Documents = internal IDs + user-facing names
- Codes = hierarchical tree
- Coded segments = ranges stored as (doc_id, start, end)

## Layers
- UI (PySide): Widgets, dialogs, views
- Application logic: CodeManager, ProjectRepository
- Storage: SQLite schema

## Key Decisions
- Integer IDs for internal FK stability
- UUIDs for export/import durability
- All project data lives under `<project_root>`
- The file list in the project view (`ProjectWidget`) right now is file system driven rather than driven by the databse. A future development is to switch over to a database driven system for displaying files in the project view.

3. Getting reports out of Mise

Mise can only be a successful analysis tool if it is capable of generating summaries or the annotated data. In essence that is what a QDA software is. But the question becomes how should it be formatted. As a first pass I think that PDFs that display the chunked annotated tags is a good start. 

## Project Schema

Work in Mise is organized around "projects", containers for documents, the project database, configuration files and metadata related to the coding and analysis being done. Each project should contain a discrete collection of data from a specific social scientific intervention.

Every project in Mise follows this schema:

```
my_project.mise/
    project.db         # SQLite, main metadata
    memos/             # Project memos
        memo_1.md
    texts/
        doc_0001.txt   # normalized UTF-8 text
        doc_0002.txt
    meta/
        codebook.json  # optional export/import format
        config.json    # view prefs, etc.
    .mise              # Software internal information
```

All information related to codes, the relationship of codes to documents, and document information is stored in an SQLite database.

## Database Schema

One of the primary differences between Mise and proprietary QDA software is that Mise uses an intelligible and transparent schema for organizing data in the database. The data base for all project information has three tables: "documents", "codes", and "coded_segments", storing information about the documents being analyzed, the codes used to analyze them, and the relationship between the two respectively.

### `documents` table 

Documents are the units of data that are being analyzed in Mise and can include interview transcripts, ethnographic field notes, or any other long form textual file with qualitative data in it. Documents on import into Mise are converted from their original format into `.txt` format, so they can be preserved in a legible and stable format.

| Column            	| Type    	| Description                                                               	|
|-------------------	|---------	|---------------------------------------------------------------------------	|
| id                	| Integer 	| Canonical unique document ID                                              	|
| original_filename 	| Text    	| The filename on import into the project                                   	|
| display_name      	| Text    	| Name displayed to user, editable                                          	|
| text_path         	| Text    	| Path to where the document is stored in /texts directory                  	|
| created_at        	| Text    	| Date document created in project                                          	|
| doc_uuid          	| Text    	| Universally Unique Identifier for export, import, and merging of projects 	|

```SQL
CREATE TABLE documents (
    id                INTEGER PRIMARY KEY,
    original_filename TEXT,
    display_name      TEXT NOT NULL,
    text_path         TEXT NOT NULL,
    created_at        TEXT NOT NULL,
    doc_uuid          TEXT UNIQUE NOT NULL
);
```

### `codes` table

Codes are the analytic objects assigned to documents in the course of creating a structured analytical framework in the project.

| Column      	| Type    	| Description                                                    	|
|-------------	|---------	|----------------------------------------------------------------	|
| id          	| Text    	| Canonical unique code ID                                       	|
| label       	| Text    	| Code name, editable                                            	|
| parent_id   	| Text    	| Code id of parent code, for sub/child codes                    	|
| description 	| Text    	| User inputed code description (optional)                       	|
| color       	| Text    	| Color associated with code for segment highlighting (optional) 	|
| sort_order  	| Integer 	| Order in which codes appear                                    	|

```SQL
CREATE TABLE codes (
    id          TEXT PRIMARY KEY,
    label       TEXT NOT NULL,
    parent_id   TEXT REFERENCES codes(id),
    description TEXT,
    color       TEXT,
    sort_order  INTEGER
);
```

### `coded_segments` table

"Coded segments" are the relationships between codes and documents.

| Column       	| Type    	| Description                            	|
|--------------	|---------	|----------------------------------------	|
| id           	| Integer 	| Canonical unique segment ID            	|
| document_id  	| Text    	| ID of document segment belongs to      	|
| code_id      	| Text    	| ID of code associated with segment     	|
| start_offset 	| Integer 	| Index in document where segment begins 	|
| end_offset   	| Integer 	| Index in document where segment ends   	|
| memo         	| Text    	| Order in which codes appear            	|
| created_at   	| Text    	| Date the segment was created           	|

```SQL
CREATE TABLE coded_segments (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id   INTEGER NOT NULL REFERENCES documents(id),
    code_id       TEXT NOT NULL REFERENCES codes(id),
    start_offset  INTEGER NOT NULL,
    end_offset    INTEGER NOT NULL,
    memo          TEXT,
    created_at    TEXT NOT NULL
);
```

## Future Features

Mise is in early development and so future versions will contain substantial changes to the UI and add features that will assit users in completing their coding and analysis projects.

### Database Versioning

Future versions of Mise will create a database versioning system so that a project would look something like this:

```sh
my-project/
  texts/
    001_interview_daniel.txt
    002_fieldnotes_icu.txt
  metadata/
    documents.csv          # doc_id, filename, participant, etc.
    codes.yaml             # hierarchical code tree
    segments.csv           # doc_id, code_id, start, end, memo_id
    memos/
      2025-11-22_clinical-ambiguity.md
  project.db               # local cache/index
```

### Project Versioning

Complimentary to database versioning, future releases of Mise will include the ability to version projects using Git. Importantly, the end-user will not have to manipulate Git directly and instead will use the UI to do this.

### Scripting and Command Line Interface

Advanced users may want to have the option to script functionality in Mise as well as manipulate certain features using a command line so we will add that as well.

## Dev Notes and `todo`

### `todo`
- need to clean up the implementation of `extract_text_from_pdf` in `src/mise/utils/file_io.py`.
- add PDF reading and conversion to `mise/utils/file_io.py` with function `read_pdf`
- Eventually, need to get a pyinstaller instance installed.
- Need to get the UI options set up, including increasing font size.
- Memoing feature, perhaps in the AnalysisWidget, and in the ProjectWidget maybe when in the document tree, a right click allows an option to open document in memo mode which allows for a two panel window where on the left is the document and on the right a text editor where you can memo.
- For analysis widget, should include an option that automatically adds to the segment which is to say expands the text selection from the document to include more context. And need some function to pull up the document from a segment.
- Folder icons not appearing in file browser
- Alembic versioning style with published schema for database
- On project creation need to add something in the root directory for the project that clearly indicates that the directory is a project file such as including a `.mise` file that has some information about under what version of the program the project was made and the author.
- For packaging the app need to set `setup_logging(..., level=logging.INFO)` in the `app.py` file.

### Proposed Order of Development

1.	Data Manager (Backend)
    - Define how documents and codes will be stored and retrieved.
    - Decide whether to use JSON, SQLite, or another format.
    - Implement basic CRUD operations for documents and codes.
    - Example: A Project class that manages documents and a Code class to store and handle codes.
    - What database to use?
2.	Text Processing
    - Implement logic for tagging and calculating co-occurrence relationships between codes.
    - This is also where algorithms for analyzing text (e.g., tokenization, counting) will live.
3.	Visualization Logic
    - Start with co-occurrence data structures and test generating NetworkX graphs from them.
    - Ensure the backend produces data that can easily plug into a visualization.
4.	Basic GUI Skeleton
    - Create a minimal GUI (main window, menus, placeholders) to test interactions with the backend.
    - Example: A basic interface to upload a document and view its contents.
5.	Incremental GUI Features
    - Build and connect each GUI feature to the backend step by step.
    - Start with simple document management and then add more complex functionality like tagging and visualization.

### Development Helpers

For visualizing dependencies

```sh
pyreverse -o png -p mise mise
pydeps mise --max-bacon=2 --show-deps

```

### Logging info

```python
log.debug("Debug info: %s", var)
log.info("Something happened: %s", var)
log.warning("This probably isn't right: %s", var)
log.error("This failed: %s", var)
log.critical("Major failure: %s", var)

try:
    risky_stuff()
except Exception:
    log.exception("Crash while doing risky_stuff")
```