from app.database import get_connection, init_db
from datetime import datetime
import pytest
import sqlite3

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
        datetime.strptime(res[3], "%Y-%m-%d %H:%M:%S")
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



def test_incorrect_relationship_creation():
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

        with pytest.raises(sqlite3.IntegrityError):
            cur.execute("INSERT INTO relationships (subject_id, predicate_id, object_id) VALUES (?, ?, ?);", (999, predicate_id[0], concept_ids[1][0]))
    finally:
        con.close()



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

        cur.execute("INSERT INTO project_concepts (concept_id, project_id) VALUES (?, ?);", (concept_id, project_id))

        res = cur.execute("SELECT * FROM project_concepts;").fetchone()

        assert res == (concept_id, project_id)
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