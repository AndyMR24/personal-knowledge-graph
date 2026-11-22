from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db
from app.routers.concepts import concept_router
from app.routers.predicates import predicate_router
from app.routers.relationships import relationship_router
from app.routers.projects import project_router
from app.routers.project_concepts import project_concept_router
from app.routers.graph import graph_router

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

@app.get("/health")
async def root():
    return {"status": "Ok"}