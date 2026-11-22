# Personal Knowledge Graph

A local web application for organizing technical learning notes as a knowledge graph. It is designed to help connect concepts across programming, SQL, data science, machine learning, and personal projects.

## Features

- **Concepts:** Create, view, update, search, and delete concepts. Each concept has a title and optional Markdown content.
- **Predicates:** Define reusable predicates to describe relationships between concepts. Predicates can be directional or bidirectional.
- **Relationships:** Connect concepts using subject–predicate–object relationships.
- **Projects:** Organize related concepts into projects.
- **Project membership:** Associate concepts with projects through a many-to-many relationship.
- **Graph retrieval:** Retrieve the full graph or the neighborhood around a specific concept.
- **Input validation:** Validate data before it reaches the database.
- **Data integrity:** Use SQLite constraints, foreign keys, duplicate checks, and transactions to protect data consistency.

The application is intended for local, single-user use. The initial focus is creating and managing a knowledge graph through an API, with graph visualization planned for the frontend.

## Technology Stack

- **Python** — application logic and data models
- **FastAPI** — REST API
- **SQLite** — persistent storage using Python's built-in `sqlite3` module
- **Pydantic** — API request validation
- **pytest** — automated testing
- **HTML, CSS, JavaScript, and Cytoscape.js** — planned frontend and graph visualization

## Data Model

The application uses five database tables.

| Table | Purpose |
|---|---|
| `concepts` | Stores concept titles and optional Markdown content |
| `predicates` | Stores reusable relationship types and their directionality |
| `relationships` | Connects a subject concept to an object concept through a predicate |
| `projects` | Stores projects with a title and optional description |
| `project_concepts` | Associates concepts with projects |

### Concepts and relationships

A relationship follows the structure:

`Subject concept → Predicate → Object concept`

For example:

`Python → used_for → Data Analysis`

Relationships reference existing concepts and predicates through foreign keys.

### Predicate directionality

Predicates have a `bidirectional` property. A bidirectional predicate can be interpreted in both directions without storing a second, reverse relationship row.

The application also supports a generic predicate without a name. This predicate must be bidirectional, and the database restricts the generic predicate to a single entry.

### Projects

Projects group concepts without requiring a separate copy of each concept. The `project_concepts` table implements the many-to-many association and prevents duplicate memberships for the same project–concept pair.

## Project Structure

The main application modules are organized by responsibility:

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
└── routers/
    ├── concepts.py
    ├── predicates.py
    ├── relationships.py
    ├── projects.py
    └── graph.py

data/
└── my_database.db

tests/
```

The exact contents of the `tests/` directory may vary as the project develops.

- `main.py` configures the FastAPI application and initializes the database during application startup.
- `database.py` manages database configuration, connections, and schema initialization.
- `dependencies.py` provides database connections to API endpoints.
- `models.py` defines validated Python dataclasses representing the application's domain entities.
- `schemas.py` defines Pydantic schemas for API request validation.
- `repositories.py` contains database operations.
- `services.py` implements application-level business logic and graph retrieval.
- `exceptions.py` defines domain exceptions used by the application.
- `routers/` contains the API endpoints grouped by resource.

## Getting Started

### Requirements

- Python 3.14 or a compatible Python version
- `pip`

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

Replace the placeholders with your repository URL and local directory name.

### 2. Create and activate a virtual environment

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

### 3. Install dependencies

Install the project's dependencies using its dependency file, if one is present:

```bash
pip install -r requirements.txt
```

### 4. Start the application

```bash
python -m uvicorn app.main:app --reload
```

FastAPI initializes the database when the application starts. The default database is stored at `data/my_database.db` relative to the project root.

Once the server is running, visit:

- **API documentation:** `http://127.0.0.1:8000/docs`
- **Alternative API documentation:** `http://127.0.0.1:8000/redoc`
- **Health check:** `http://127.0.0.1:8000/health`

## API Overview

The API provides CRUD operations for concepts, predicates, relationships, and projects, as well as operations for managing project memberships.

| Resource | Base path | Capabilities |
|---|---|---|
| Concepts | `/concepts` | List/search, create, retrieve, update, delete |
| Predicates | `/predicates` | List, create, retrieve, update, delete |
| Relationships | `/relationships` | List, create, retrieve, update, delete |
| Projects | `/projects` | List/search by title, create, retrieve, update, delete |
| Project memberships | `/projects/{project_id}/concepts` | Add or remove a concept from a project |
| Full graph | `/graph/` | Retrieve graph data for the application |
| Concept neighborhood | `/concepts/{concept_id}/neighborhood` | Retrieve the neighborhood of a concept |

For exact request schemas and response formats, use the interactive API documentation at `/docs`.

### Graph endpoints

The graph endpoints return five collections:

- `concepts`
- `relationships`
- `predicates`
- `projects`
- `project_concepts`

The full graph endpoint returns the graph data across all five collections.

The concept neighborhood endpoint returns the selected concept and its direct neighbors, the relevant relationships and predicates, and projects directly associated with the selected concept. It does not expand project memberships to include projects associated only with neighboring concepts.

These responses provide the data needed for graph visualization while leaving frontend presentation choices independent of the API.

### API behavior

- Successful creation requests return HTTP `201`.
- Successful deletion requests return HTTP `204`.
- Missing resources return HTTP `404`.
- Duplicate or conflicting operations return HTTP `409`.
- Invalid request data is rejected with HTTP `422`.
- Collection requests return an empty list when there are no matching results.

Write endpoints commit successful transactions and roll back failed operations.

## Data Validation and Integrity

The application separates API request validation, domain models, business logic, and database operations.

- Pydantic schemas validate incoming API data.
- Domain dataclasses validate values independently of FastAPI and SQLite.
- Services handle application-level rules such as existence checks and duplicate prevention.
- Repositories perform database operations using an explicitly supplied connection.
- SQLite foreign keys and constraints enforce referential integrity and uniqueness.

Database connections enable foreign-key enforcement. The repository layer does not commit transactions; transaction control is handled by the endpoint layer.

## Running Tests

Run the automated test suite from the project root:

```bash
python -m pytest
```

To see more detailed test output:

```bash
python -m pytest -v
```

## Current Scope and Future Work

The current milestone establishes the data model, persistence layer, domain validation, business logic, CRUD API, project memberships, and graph retrieval endpoints.

Potential future improvements include:

- Building the web frontend.
- Visualizing the graph with Cytoscape.js.
- Adding controls to explore neighborhoods and toggle project nodes.
- Supporting import and export of existing Markdown or plain-text notes.
- Implementing reliable database backup and restore workflows.
- Expanding project-based exploration and filtering.

## Known TODOs

- Decide how `ProjectUpdate` should handle an explicitly supplied `null` title. The intended behavior needs to be defined and tested before considering this edge case fully resolved.