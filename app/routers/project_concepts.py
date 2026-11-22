from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_db
from app.exceptions import DuplicateError, NotFoundError
from app.models import ProjectConcept
from app.repositories import (
    get_project_concept_by_id,
    get_all_project_concepts
)
from app.services import (
    create_project_concept,
    update_project_concept,
    delete_project_concept
)
from app.schemas import ProjectConceptCreate
import sqlite3

project_concept_router = APIRouter(prefix="/project_concepts", tags=["project_concepts"])

@project_concept_router.get("/{project_concept_id}")
def get_concept_project_by_id_endpoint(
    project_concept_id: int,
    con: sqlite3.Connection = Depends(get_db)
) -> ProjectConcept:

    project_concept = get_project_concept_by_id(con, project_concept_id)

    if project_concept is None:
        raise HTTPException(404, "The concept is not associated to this project")

    return project_concept



@project_concept_router.get("/")
def get_all_project_concepts_endpoint(
    con: sqlite3.Connection = Depends(get_db)
) -> list[ProjectConcept]:
    
    return get_all_project_concepts(con)



@project_concept_router.post("/", status_code=201)
def create_project_concept_endpoint(
    project_concept_schema: ProjectConceptCreate,
    con: sqlite3.Connection = Depends(get_db)
) -> ProjectConcept:
    
    new_concept = ProjectConcept(concept_id=project_concept_schema.concept_id, project_id=project_concept_schema.project_id)

    try:
        created_project_concept = create_project_concept(con, new_concept)
        con.commit()
    except DuplicateError as exception:
        con.rollback()
        raise HTTPException(409, detail=str(exception))
    except NotFoundError as exception:
        con.rollback()
        raise HTTPException(404, detail=exception)
    except Exception:
        con.rollback()
        raise

    return created_project_concept



@project_concept_router.delete("/{project_concept_id}", status_code=204)
def delete_project_concept_endpoint(
    project_concept_id: int,
    con: sqlite3.Connection = Depends(get_db)
) -> None:

    try:
        delete_project_concept(con, project_concept_id)
        con.commit()
    except NotFoundError as exception:
        con.rollback()
        raise HTTPException(404, detail=str(exception))
    except Exception:
        con.rollback()
        raise