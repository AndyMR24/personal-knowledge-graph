from app.database import get_connection

def get_db():
    con = get_connection()

    try:
        yield con
    finally:
        con.close()