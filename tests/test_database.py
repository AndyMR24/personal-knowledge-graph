from app.database import get_connection, init_db
import pytest
import sqlite3


@pytest.fixture
def initialized_db():
    con = get_connection(":memory:")
    init_db(con)

    try:
        yield con
    finally:
        con.close()


def test_parent_directory_creation(tmp_path):
    tmp_db_path = tmp_path / "test_data" / "test.db"

    assert not tmp_db_path.parent.exists()

    con = get_connection(tmp_db_path)

    try:
        assert tmp_db_path.parent.exists()
    finally:
        con.close()



def test_foreign_key_enforcement():
    con = get_connection(":memory:")

    try:
        assert con.execute("PRAGMA foreign_keys;").fetchone() == (1,)
    finally:
        con.close()



def test_concept_creation():
    con = get_connection(":memory:")
    cur = con.cursor()

    try:
        init_db(con)

        cur.execute("INSERT INTO concepts (title) VALUES (?);", ('Python',))
        
        res =  cur.execute("SELECT * FROM concepts;").fetchone()

        assert res[0] == 1
        assert res[1] == 'Python'
    finally:
        con.close()



def test_duplicated_predicate_names():
    con = get_connection(":memory:")
    cur = con.cursor()

    try:
        init_db(con)

        with pytest.raises(sqlite3.IntegrityError):
            cur.execute("INSERT INTO predicates (name) VALUES" \
                "(?)," \
                "(?);", ('isA', 'isA',))
    finally:
        con.close()


def test_generic_predicate_defaults_to_bidirectional(initialized_db):
    cur = initialized_db.cursor()

    cur.execute("INSERT INTO predicates DEFAULT VALUES;")

    assert cur.execute(
        "SELECT name, bidirectional FROM predicates;"
    ).fetchone() == (None, 1)


def test_second_generic_predicate_is_rejected(initialized_db):
    cur = initialized_db.cursor()
    cur.execute("INSERT INTO predicates DEFAULT VALUES;")

    with pytest.raises(sqlite3.IntegrityError):
        cur.execute(
            "INSERT INTO predicates (name, bidirectional) VALUES (NULL, 1);"
        )


def test_generic_predicate_must_be_bidirectional(initialized_db):
    cur = initialized_db.cursor()

    with pytest.raises(sqlite3.IntegrityError):
        cur.execute(
            "INSERT INTO predicates (name, bidirectional) VALUES (NULL, 0);"
        )


@pytest.mark.parametrize("bidirectional", [0, 1])
def test_named_predicate_accepts_boolean_directionality(
    initialized_db, bidirectional
):
    cur = initialized_db.cursor()

    cur.execute(
        "INSERT INTO predicates (name, bidirectional) VALUES (?, ?);",
        ("related_to", bidirectional),
    )

    assert cur.execute(
        "SELECT bidirectional FROM predicates WHERE name = ?;",
        ("related_to",),
    ).fetchone() == (bidirectional,)



def test_relationship_creation():
    con = get_connection(":memory:")
    cur = con.cursor()

    try:
        init_db(con)

        assert cur.execute("PRAGMA foreign_keys;").fetchone() == (1,)

        cur.execute("INSERT INTO concepts (title)" \
            "VALUES (?), (?);", ('Python', 'Unit Tests',))

        cur.execute("INSERT INTO predicates (name)" \
        "VALUES (?);", ('uses',))

        concept_ids = cur.execute("SELECT id FROM concepts ORDER BY id;").fetchall()

        predicate_id = cur.execute("SELECT id FROM predicates;").fetchone()

        cur.execute("INSERT INTO relationships (subject_id, predicate_id, object_id) VALUES (?, ?, ?);", (concept_ids[0][0], predicate_id[0], concept_ids[1][0]))

        res = cur.execute("SELECT * FROM relationships;").fetchone()

        assert res == (1, concept_ids[0][0], predicate_id[0], concept_ids[1][0], None)
    finally:
        con.close()



@pytest.mark.parametrize(
    "invalid_field",
    ["subject_id", "predicate_id", "object_id"],
)
def test_relationship_rejects_invalid_foreign_keys(
    initialized_db, invalid_field
):
    cur = initialized_db.cursor()
    cur.execute(
        "INSERT INTO concepts (id, title) VALUES (1, ?), (2, ?);",
        ("Python", "Unit Tests"),
    )
    cur.execute(
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
        cur.execute(
            "INSERT INTO relationships "
            "(subject_id, predicate_id, object_id) "
            "VALUES (:subject_id, :predicate_id, :object_id);",
            relationship,
        )



def test_project_creation():
    con = get_connection(":memory:")
    cur = con.cursor()

    try:
        init_db(con)

        assert cur.execute("PRAGMA foreign_keys;").fetchone() == (1,)

        cur.execute("INSERT INTO projects (title, description) VALUES" \
            "(?, ?);", ('Thesis', 'My thesis',))

        res = cur.execute("SELECT * FROM projects;").fetchone()

        assert res == (1, 'Thesis', 'My thesis')
    finally:
        con.close()



def test_project_concept_creation():
    con = get_connection(":memory:")
    cur = con.cursor()

    try:
        init_db(con)

        cur.execute("INSERT INTO concepts (id, title) VALUES" \
            "(?, ?);", (2, 'Python'))

        cur.execute("INSERT INTO projects (title) VALUES" \
            "(?);", ('Thesis',))

        concept_id = cur.execute("SELECT id FROM concepts;").fetchone()[0]

        project_id = cur.execute("SELECT id FROM projects;").fetchone()[0]

        cur.execute("INSERT INTO project_concepts VALUES (?, ?, ?);", (1, concept_id, project_id))

        project_concept_id = cur.execute("SELECT id FROM project_concepts;").fetchone()[0]

        res = cur.execute("SELECT * FROM project_concepts;").fetchone()

        assert res == (project_concept_id, concept_id, project_id)
    finally:
        con.close()



def test_pcc_with_nonexistent_concept_id():
    con = get_connection(":memory:")
    cur = con.cursor()

    try:
        init_db(con)

        cur.execute("INSERT INTO projects (title) VALUES" \
            "(?);", ('Thesis',))

        project_id = cur.execute("SELECT id FROM projects;").fetchone()[0]

        with pytest.raises(sqlite3.IntegrityError):
            cur.execute("INSERT INTO project_concepts (concept_id, project_id) VALUES (?, ?);", (999, project_id))
    finally:
        con.close()



def test_pcc_with_nonexistent_project_id():
    con = get_connection(":memory:")
    cur = con.cursor()

    try:
        init_db(con)

        cur.execute("INSERT INTO concepts (title) VALUES" \
            "(?);", ('Python',))

        concept_id = cur.execute("SELECT id FROM concepts;").fetchone()[0]

        with pytest.raises(sqlite3.IntegrityError):
            cur.execute("INSERT INTO project_concepts (concept_id, project_id) VALUES (?, ?);", (concept_id, 999))
    finally:
        con.close()



def test_duplicate_project_concept_creation():
    con = get_connection(":memory:")
    cur = con.cursor()

    try:
        init_db(con)

        cur.execute("INSERT INTO concepts (id, title) VALUES" \
            "(?, ?);", (2, 'Python'))

        cur.execute("INSERT INTO projects (title) VALUES" \
            "(?);", ('Thesis',))

        concept_id = cur.execute("SELECT id FROM concepts;").fetchone()[0]

        project_id = cur.execute("SELECT id FROM projects;").fetchone()[0]

        cur.execute("INSERT INTO project_concepts (concept_id, project_id) VALUES (?, ?);", (concept_id, project_id))

        with pytest.raises(sqlite3.IntegrityError):
            cur.execute("INSERT INTO project_concepts (concept_id, project_id) VALUES (?, ?);", (concept_id, project_id))
    finally:
        con.close()
