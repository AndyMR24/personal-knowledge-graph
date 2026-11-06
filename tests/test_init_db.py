from app.database import get_connection, init_db

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


def test_db_initialization():
    con = get_connection(":memory:")
    cur = con.cursor()

    try:
        init_db(con)

        res = cur.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )

        stored_tables = {row[0] for row in res.fetchall()}

        assert stored_tables == EXPECTED_TABLES
    finally:
        con.close()


def test_db_schema_matches_confirmed_design():
    con = get_connection(":memory:")

    try:
        init_db(con)

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
            "remarks": 0,
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
    finally:
        con.close()


def test_db_initialization_is_idempotent():
    con = get_connection(":memory:")

    try:
        init_db(con)
        schema_before = con.execute(
            "SELECT type, name, tbl_name, sql FROM sqlite_master "
            "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
        ).fetchall()

        init_db(con)
        schema_after = con.execute(
            "SELECT type, name, tbl_name, sql FROM sqlite_master "
            "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
        ).fetchall()

        assert schema_after == schema_before
    finally:
        con.close()
