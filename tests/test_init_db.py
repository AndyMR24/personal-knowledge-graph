from app.database import get_connection, init_db
import pytest
import sqlite3


@pytest.fixture
def initialized_db():
    con = get_connection(":memory:")

    try:
        init_db(con)
        yield con
    finally:
        con.close()


EXPECTED_TABLES = {
    "concepts",
    "predicates",
    "relationships",
    "projects",
    "project_concepts",
}


def _table_info(con, table_name):
    return con.execute(f"PRAGMA table_info({table_name})").fetchall()


def _index_columns(con, index_name):
    return tuple(
        row[2] for row in con.execute(f"PRAGMA index_info({index_name})")
    )


def test_db_initialization(initialized_db):
    res = initialized_db.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
    )

    stored_tables = {row[0] for row in res.fetchall()}

    assert stored_tables == EXPECTED_TABLES


def test_db_schema_matches_confirmed_design(initialized_db):
    con = initialized_db

    for table_name in EXPECTED_TABLES - {"project_concepts"}:
        primary_key = [
            row[1] for row in _table_info(con, table_name) if row[5]
        ]
        assert primary_key == ["id"]

    concept_columns = {
        row[1]: row[3] for row in _table_info(con, "concepts")
    }
    assert concept_columns == {
        "id": 0,
        "title": 1,
        "content": 0,
    }

    predicate_columns = {
        row[1]: (row[3], row[4])
        for row in _table_info(con, "predicates")
    }
    assert predicate_columns["name"] == (0, None)
    assert predicate_columns["bidirectional"] == (1, "1")

    relationship_columns = {
        row[1]: row[3]
        for row in _table_info(con, "relationships")
    }
    assert relationship_columns == {
        "id": 0,
        "subject_id": 1,
        "predicate_id": 1,
        "object_id": 1,
    }

    project_columns = {
        row[1]: row[3] for row in _table_info(con, "projects")
    }
    assert project_columns == {
        "id": 0,
        "title": 1,
        "description": 0,
    }

    project_concept_info = _table_info(con, "project_concepts")
    assert [(row[1], row[3], row[5]) for row in project_concept_info] == [
        ("id", 0, 1),
        ("concept_id", 1, 0),
        ("project_id", 1, 0),
    ]

    unique_index_columns = [
        _index_columns(con, row[1])
        for row in con.execute("PRAGMA index_list(project_concepts)")
        if row[2]
    ]
    assert ("concept_id", "project_id") in unique_index_columns

    relationship_foreign_keys = {
        (row[3], row[2], row[4])
        for row in con.execute("PRAGMA foreign_key_list(relationships)")
    }
    assert relationship_foreign_keys == {
        ("subject_id", "concepts", "id"),
        ("predicate_id", "predicates", "id"),
        ("object_id", "concepts", "id"),
    }

    project_concept_foreign_keys = {
        (row[3], row[2], row[4])
        for row in con.execute(
            "PRAGMA foreign_key_list(project_concepts)"
        )
    }
    assert project_concept_foreign_keys == {
        ("concept_id", "concepts", "id"),
        ("project_id", "projects", "id"),
    }


def test_db_initialization_is_idempotent(initialized_db):
    schema_before = initialized_db.execute(
        "SELECT type, name, tbl_name, sql FROM sqlite_master "
        "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
    ).fetchall()

    init_db(initialized_db)
    schema_after = initialized_db.execute(
        "SELECT type, name, tbl_name, sql FROM sqlite_master "
        "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
    ).fetchall()

    assert schema_after == schema_before


def test_duplicated_predicate_names_are_rejected(initialized_db):
    with pytest.raises(sqlite3.IntegrityError):
        initialized_db.execute(
            "INSERT INTO predicates (name) VALUES (?), (?);",
            ("isA", "isA"),
        )


def test_generic_predicate_defaults_to_bidirectional(initialized_db):
    initialized_db.execute("INSERT INTO predicates DEFAULT VALUES;")

    assert initialized_db.execute(
        "SELECT name, bidirectional FROM predicates;"
    ).fetchone() == (None, 1)


def test_second_generic_predicate_is_rejected(initialized_db):
    initialized_db.execute("INSERT INTO predicates DEFAULT VALUES;")

    with pytest.raises(sqlite3.IntegrityError):
        initialized_db.execute(
            "INSERT INTO predicates (name, bidirectional) VALUES (NULL, 1);"
        )


def test_generic_predicate_must_be_bidirectional(initialized_db):
    with pytest.raises(sqlite3.IntegrityError):
        initialized_db.execute(
            "INSERT INTO predicates (name, bidirectional) VALUES (NULL, 0);"
        )


@pytest.mark.parametrize("bidirectional", [0, 1])
def test_named_predicate_accepts_boolean_directionality(
    initialized_db,
    bidirectional,
):
    initialized_db.execute(
        "INSERT INTO predicates (name, bidirectional) VALUES (?, ?);",
        ("related_to", bidirectional),
    )

    assert initialized_db.execute(
        "SELECT bidirectional FROM predicates WHERE name = ?;",
        ("related_to",),
    ).fetchone() == (bidirectional,)


@pytest.mark.parametrize("bidirectional", [-1, 2])
def test_predicate_rejects_invalid_stored_directionality(
    initialized_db,
    bidirectional,
):
    with pytest.raises(sqlite3.IntegrityError):
        initialized_db.execute(
            "INSERT INTO predicates (name, bidirectional) VALUES (?, ?);",
            ("related_to", bidirectional),
        )


@pytest.mark.parametrize(
    "invalid_field",
    ["subject_id", "predicate_id", "object_id"],
)
def test_relationship_rejects_invalid_foreign_keys(
    initialized_db,
    invalid_field,
):
    initialized_db.execute(
        "INSERT INTO concepts (id, title) VALUES (1, ?), (2, ?);",
        ("Python", "Unit Tests"),
    )
    initialized_db.execute(
        "INSERT INTO predicates (id, name) VALUES (1, ?);",
        ("uses",),
    )

    relationship = {
        "subject_id": 1,
        "predicate_id": 1,
        "object_id": 2,
    }
    relationship[invalid_field] = 999

    with pytest.raises(sqlite3.IntegrityError):
        initialized_db.execute(
            "INSERT INTO relationships "
            "(subject_id, predicate_id, object_id) "
            "VALUES (:subject_id, :predicate_id, :object_id);",
            relationship,
        )


@pytest.mark.parametrize("invalid_field", ["concept_id", "project_id"])
def test_project_concept_rejects_invalid_foreign_keys(
    initialized_db,
    invalid_field,
):
    concept_id = initialized_db.execute(
        "INSERT INTO concepts (title) VALUES (?);",
        ("Python",),
    ).lastrowid
    project_id = initialized_db.execute(
        "INSERT INTO projects (title) VALUES (?);",
        ("Thesis",),
    ).lastrowid

    project_concept = {
        "concept_id": concept_id,
        "project_id": project_id,
    }
    project_concept[invalid_field] = 999

    with pytest.raises(sqlite3.IntegrityError):
        initialized_db.execute(
            "INSERT INTO project_concepts (concept_id, project_id) "
            "VALUES (:concept_id, :project_id);",
            project_concept,
        )


def test_duplicate_project_concept_is_rejected(initialized_db):
    concept_id = initialized_db.execute(
        "INSERT INTO concepts (title) VALUES (?);",
        ("Python",),
    ).lastrowid
    project_id = initialized_db.execute(
        "INSERT INTO projects (title) VALUES (?);",
        ("Thesis",),
    ).lastrowid
    initialized_db.execute(
        "INSERT INTO project_concepts (concept_id, project_id) "
        "VALUES (?, ?);",
        (concept_id, project_id),
    )

    with pytest.raises(sqlite3.IntegrityError):
        initialized_db.execute(
            "INSERT INTO project_concepts (concept_id, project_id) "
            "VALUES (?, ?);",
            (concept_id, project_id),
        )
