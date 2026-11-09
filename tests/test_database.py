from app.database import get_connection


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
