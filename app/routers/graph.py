from fastapi import APIRouter, Depends
from app.dependencies import get_db
from app.models import GraphResult
from app.services import get_full_graph
import sqlite3

graph_router = APIRouter(prefix="/graph", tags=["graph"])

@graph_router.get("/")
def get_full_graph_router(con: sqlite3.Connection = Depends(get_db)) -> GraphResult:
    return get_full_graph(con)
    