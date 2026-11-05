from app.database import get_connection, init_db

def test_db_initialization():
    con = get_connection(":memory:")
    cur = con.cursor()

    try:
        init_db(con)

        res = cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")

        stored_tables = res.fetchall()
        
        assert ("concepts",) in stored_tables
        assert ("predicates",) in stored_tables
        assert ("relationships",) in stored_tables
        assert ("projects",) in stored_tables
        assert ("project_concepts",) in stored_tables
    finally:
        con.close()