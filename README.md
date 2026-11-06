# Personal Knowledge Graph

A local, single-user application for organizing knowledge as a graph of concepts and their relationships.

The goal is to create a structured knowledge base where concepts can be documented, connected to one another, and organized into projects. A graph visualization will eventually make it easier to explore how different pieces of knowledge relate.

## Current Status

The project is in early development.

Currently implemented:
- FastAPI application with a health-check endpoint.
- SQLite database initialization.
- Database schema for concepts, predicates, relationships, projects, and project–concept associations.
- Domain models and validation rules for concepts, predicates, relationships, projects, and project–concept associations.
- Automated tests for database behavior and integrity constraints.

Features such as creating and editing concepts through a web interface and visualizing the knowledge graph are planned for future milestones.

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
│   └── models.py
├── tests/
├── data/
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

- `app/main.py` contains the FastAPI application.
- `app/database.py` handles database connections and schema initialization.
- `app/models.py` contains the domain dataclasses and validation rules.
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

- Application: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs

The database schema is initialized when the application starts.

To stop the development server, press `Ctrl+C`.

## Running Tests

Run the test suite from the repository root:

```bash
python -m pytest
```

Database tests use in-memory SQLite databases where appropriate and isolated temporary filesystem paths where necessary, keeping test data separate from the application's local database.

## Data Model

The current database schema consists of five tables:

| Table | Purpose |
|---|---|
| `concepts` | Stores concepts and their optional content. |
| `predicates` | Stores reusable relationship types, their directionality, and the optional generic predicate. |
| `relationships` | Connects concepts through predicates. |
| `projects` | Stores projects with titles and optional descriptions. |
| `project_concepts` | Associates concepts with projects using a unique concept–project pair. |

A concept can belong to multiple projects or exist independently of any project. Relationships reference concepts and predicates through foreign keys. Project–concept associations use an `id` primary key and a `UNIQUE(concept_id, project_id)` constraint to prevent duplicate pairs. A predicate with a `NULL` name is the single generic predicate and must be bidirectional.

## Development Philosophy

The project prioritizes:

- Simplicity and maintainability.
- Reliable data storage and integrity.
- Clear separation between concepts, relationships, and project organization.
- Automated testing of important database behavior.
- Incremental development and learning.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
