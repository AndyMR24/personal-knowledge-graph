from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from app.database import init_db
from app.routers.concepts import concept_router
from app.routers.predicates import predicate_router
from app.routers.relationships import relationship_router
from app.routers.projects import project_router
from app.routers.project_concepts import project_concept_router
from app.routers.graph import graph_router

ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_FOLDER_PATH = ROOT_DIR / "app" / "static"
TEMPLATES_FOLDER_PATH = ROOT_DIR / "app" / "templates"

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan = lifespan)

app.include_router(concept_router)
app.include_router(predicate_router)
app.include_router(relationship_router)
app.include_router(project_router)
app.include_router(project_concept_router)
app.include_router(graph_router)

app.mount("/static", StaticFiles(directory=STATIC_FOLDER_PATH), name="static")

@app.get("/", response_class=FileResponse)
async def main_page():
    return TEMPLATES_FOLDER_PATH / "index.html"

@app.get("/health")
async def root():
    return {"status": "Ok"}