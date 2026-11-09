from pathlib import Path
import sqlite3

ROOT_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = ROOT_DIR / "data" / "my_database.db"

def get_connection(db_path: Path | str = DATABASE_PATH) -> sqlite3.Connection:
    if db_path != ":memory:":
        Path(db_path).parent.mkdir(parents = True, exist_ok = True)

    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON;")

    return con

def init_db(con = None) -> None:
    own_connection = con is None
    
    if own_connection:
        con = get_connection()
    
    cur = con.cursor()

    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS concepts(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT);
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS predicates(
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            bidirectional INTEGER NOT NULL DEFAULT 1
                CHECK (bidirectional IN (0, 1)),
            CHECK (name IS NOT NULL OR bidirectional = 1));
        """)

        # Enforce only one predicate has a NULL name
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_predicates_single_generic
            ON predicates((1))
            WHERE name IS NULL;
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS relationships(
            id INTEGER PRIMARY KEY,
            subject_id INTEGER NOT NULL REFERENCES concepts(id),
            predicate_id INTEGER NOT NULL REFERENCES predicates(id),
            object_id INTEGER NOT NULL REFERENCES concepts(id));
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT);
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS project_concepts(
            id INTEGER PRIMARY KEY,
            concept_id INTEGER NOT NULL REFERENCES concepts(id),
            project_id INTEGER NOT NULL REFERENCES projects(id),
            UNIQUE (concept_id, project_id));
        """)

        con.commit()
    finally:
        if own_connection:
            con.close()