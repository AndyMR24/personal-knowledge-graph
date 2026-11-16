# Personal Knowledge Graph

A local, single-user application for organizing knowledge as a graph of concepts and their relationships.

The goal is to create a structured knowledge base where concepts can be documented, connected to one another, and organized into projects. A graph visualization will eventually make it easier to explore how different pieces of knowledge relate.

## Current Status

The project is under active development.

Currently implemented:

- FastAPI application with a health-check endpoint.
- SQLite database connections, schema initialization, and foreign-key enforcement.
- Database schema for concepts, predicates, relationships, projects, and project–concept associations.
- Validated domain models implemented as Python dataclasses.
- Repository layer with CRUD operations for all five entities.
- Service layer for application-level operations, including relationship validation, concept deletion with dependent-record cleanup, and project–concept associations.
- Concept search by title using substring matching.
- Full graph retrieval, returning all concepts and relationships.
- Neighborhood retrieval, returning a selected concept, its directly connected neighbors, and the relevant incoming and outgoing relationships.
- Automated tests covering domain validation, database integrity, repository operations, service logic, and graph queries.

The current focus is the backend and its data-access and application logic. A web interface for managing knowledge and an interactive graph visualization are planned for future development.

## Technology Stack

- **Python** — application logic
- **FastAPI** — backend web framework
- **Uvicorn** — ASGI server
- **SQLite** — database
- **pytest** — automated testing
- **HTML, CSS, and JavaScript** — planned frontend
- **Cytoscape.js** — planned graph visualization

## Project Structure

```text
personal-knowledge-graph/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── repositories.py
│   └── services.py
├── tests/
├── data/
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

- `app/main.py` contains the FastAPI application.
- `app/database.py` handles database connections and schema initialization.
- `app/models.py` defines the domain dataclasses and their validation rules.
- `app/repositories.py` implements database operations for creating, retrieving, updating, and deleting entities, as well as supporting queries.
- `app/services.py` implements application-level operations and business rules by coordinating repository functions.
- `tests/` contains automated tests.
- `data/` is reserved for local application data, including the SQLite database.

## Requirements

- Python 3.14 or another compatible Python version.
- pip

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd personal-knowledge-graph
```

Replace `<repository-url>` with the repository's actual URL.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Running the Application

From the repository root, run:

```bash
python -m uvicorn app.main:app --reload
```

The application will be available locally at:

- Application: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

The database schema is initialized when the application starts.

To stop the development server, press `Ctrl+C`.

## Running Tests

Run the test suite from the repository root:

```bash
python -m pytest
```

Database tests use in-memory SQLite databases where appropriate and isolated temporary filesystem paths where necessary, keeping test data separate from the application's local database.

## Data Model

The database schema consists of five tables:

| Table | Purpose |
|---|---|
| `concepts` | Stores concepts and their optional content. |
| `predicates` | Stores reusable relationship types, their directionality, and the optional generic predicate. |
| `relationships` | Connects concepts through predicates. |
| `projects` | Stores projects with titles and optional descriptions. |
| `project_concepts` | Associates concepts with projects using a unique concept–project pair. |

A concept can belong to multiple projects or exist independently of any project. Relationships reference concepts and predicates through foreign keys.

The `project_concepts` table uses an `id` primary key and a `UNIQUE(concept_id, project_id)` constraint to prevent duplicate associations. A predicate with a `NULL` name represents the single generic predicate and must be bidirectional.

## Current Backend Capabilities

- **Concept management:** Create, retrieve, update, and delete concepts.
- **Predicate management:** Manage reusable relationship types and their directionality.
- **Relationship management:** Create, retrieve, update, and delete relationships while enforcing application-level validation rules.
- **Project management:** Create, retrieve, update, and delete projects.
- **Project–concept associations:** Associate concepts with projects and remove those associations without deleting the concepts themselves.
- **Concept search:** Find concepts by title using substring matching.
- **Graph retrieval:** Retrieve the full graph or explore the immediate neighborhood of a specific concept.

These capabilities are currently implemented in the backend; a user-facing interface for them remains planned.

## Development Philosophy

The project prioritizes:

- Simplicity and maintainability.
- Reliable data storage and integrity.
- Clear separation between domain models, database operations, and application logic.
- Automated testing of important behavior.
- Incremental development and learning.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.