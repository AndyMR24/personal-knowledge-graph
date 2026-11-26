# Personal Knowledge Graph

A local, single-user web application for organizing technical concepts, notes, relationships, and projects as an interactive knowledge graph.

For interface instructions and daily workflows, see [USER_MANUAL.md](USER_MANUAL.md).

## Features

- Interactive Cytoscape.js graph with concept and project nodes
- Search, pan, zoom, recentering, and project visibility controls
- CRUD workflows for concepts, projects, predicates, and relationships
- Project membership management from the graph interface
- Markdown rendering for concept notes and project descriptions
- Contextual detail panels with editing and deletion controls
- Inline predicate creation while creating a relationship
- Safe rendering with raw HTML treated as text and URL-scheme filtering
- Validation, duplicate detection, confirmations, loading states, and error feedback

The application currently requires internet access for the pinned Cytoscape.js CDN asset.

## Technology Stack

- **Python**
- **FastAPI**
- **SQLite** using Python's built-in `sqlite3`
- **Pydantic**
- **pytest**
- **Vanilla HTML, CSS, and JavaScript**
- **Cytoscape.js** loaded from jsDelivr

## Data Model

| Table | Purpose |
|---|---|
| `concepts` | Concept titles and optional Markdown content |
| `predicates` | Reusable relationship types and directionality |
| `relationships` | Subject–predicate–object connections between concepts |
| `projects` | Project titles and optional Markdown descriptions |
| `project_concepts` | Many-to-many concept membership in projects |

A relationship has the shape `subject → predicate → object`. Bidirectional predicates apply in both directions without a second stored row. An unnamed predicate is supported only in bidirectional form, and the database allows at most one unnamed predicate.

Project deletion removes the project's membership rows before deleting the project. The operation uses a SQLite savepoint so a failure after membership removal restores the project and memberships.

## Project Structure

```text
app/
├── main.py
├── database.py
├── dependencies.py
├── models.py
├── schemas.py
├── repositories.py
├── services.py
├── exceptions.py
├── routers/
│   ├── concepts.py
│   ├── predicates.py
│   ├── relationships.py
│   ├── projects.py
│   ├── project_concepts.py
│   └── graph.py
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/
        ├── api.js
        ├── crud.js
        ├── graph-view.js
        ├── main.js
        ├── markdown.js
        ├── palette.js
        └── ui.js

data/
└── my_database.db

tests/
```

The frontend has no build step. FastAPI serves the template and static assets directly.

### Frontend responsibilities

- `main.js` owns application state, detail-panel content, search, graph refresh, and header personalization.
- `graph-view.js` maps API graph data into Cytoscape elements and handles node, edge, project, and layout behavior.
- `crud.js` contains the forms and mutation workflows built on the existing API.
- `api.js` centralizes request handling and API error normalization.
- `markdown.js` renders Markdown through DOM nodes without executing stored HTML.
- `ui.js` provides dialogs, conditional forms, confirmations, custom listboxes, and notifications.
- `palette.js` assigns stable color tones to graph entities.

## Setup

### Requirements

- Python 3.14 or a compatible version
- `pip`

### Create a virtual environment

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python -m uvicorn app.main:app --reload
```

The application is available at:

- **Web application:** `http://127.0.0.1:8000/`
- **API documentation:** `http://127.0.0.1:8000/docs`
- **Alternative API documentation:** `http://127.0.0.1:8000/redoc`
- **Health check:** `http://127.0.0.1:8000/health`

The default SQLite database is `data/my_database.db`.

## API Overview

| Resource | Base path | Operations |
|---|---|---|
| Concepts | `/concepts/` | list/search, create, retrieve, update, delete |
| Predicates | `/predicates/` | list, create, retrieve, update, delete |
| Relationships | `/relationships/` | list, create, retrieve, update, delete |
| Projects | `/projects/` | list/search, create, retrieve, update, delete |
| Project memberships | `/project_concepts/` | list, create, retrieve, delete |
| Full graph | `/graph/` | retrieve all graph collections |
| Concept neighborhood | `/concepts/{concept_id}/neighborhood` | retrieve a concept's direct graph context |

Graph responses contain `concepts`, `predicates`, `relationships`, `projects`, and `project_concepts`.

API behavior:

- `201` for successful creation
- `204` for successful deletion
- `404` for missing resources
- `409` for duplicates or conflicts
- `422` for invalid request data

## Validation and Transaction Behavior

Pydantic schemas validate API input, domain dataclasses validate application values, services enforce business rules, and repositories perform SQL operations.

- SQLite foreign keys are enabled for every connection.
- Repositories do not commit transactions.
- Endpoint handlers commit successful writes and roll back failures.
- Concept and predicate deletion remove dependent relationships.
- Concept deletion removes project memberships.
- Project deletion removes its memberships inside a rollback-capable savepoint.

## Testing

Run the complete test suite:

```bash
python -m pytest
```

Run with expanded output:

```bash
python -m pytest -v
```

The tests use in-memory or temporary databases and do not seed the personal database.

## Current Scope and Future Work

The implemented scope includes the CRUD API, graph persistence, web interface, interactive graph exploration, safe Markdown rendering, and the main knowledge-management workflows.

Potential future work:

- Bundle Cytoscape.js locally for offline use
- Import and export Markdown notes
- Database backup and restore workflows
- More advanced graph filtering and layout options
- Automated browser test coverage
