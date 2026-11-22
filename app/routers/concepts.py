from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_db
from app.exceptions import NotFoundError
from app.models import Concept, GraphResult
from app.repositories import (
    create_concept,
    get_concept_by_id,
    update_concept,
    search_concepts_by_title,
    get_all_concepts
)
from app.services import delete_concept, get_concept_neighborhood
from app.schemas import ConceptCreate, ConceptUpdate
import sqlite3

concept_router = APIRouter(prefix="/concepts", tags=["concepts"])

@concept_router.get("/{concept_id}")
def get_concept_by_id_endpoint(
    concept_id: int,
    con: sqlite3.Connection = Depends(get_db)
) -> Concept:
    
    concept = get_concept_by_id(con, concept_id)

    if concept is None:
        raise HTTPException(404, "The concept does not exist")

    return concept



@concept_router.get("/{concept_id}/neighborhood")
def get_concept_neighborhood_endpoint(
    concept_id: int,
    con: sqlite3.Connection = Depends(get_db)
) -> GraphResult:

    try:
       return get_concept_neighborhood(con, concept_id)
    except NotFoundError as exception:
        raise HTTPException(404, detail=str(exception))
    except Exception:
        raise
    


@concept_router.get("/")
def get_all_concepts_endpoint(
    title: str | None = None,
    con: sqlite3.Connection = Depends(get_db)
) -> list[Concept]:
    
    return get_all_concepts(con) if title is None else search_concepts_by_title(con, title)



@concept_router.post("/", status_code=201)
def create_concept_endpoint(
    concept_schema: ConceptCreate,
    con: sqlite3.Connection = Depends(get_db)
) -> Concept:
    
    new_concept = Concept(title=concept_schema.title, content=concept_schema.content)

    try:
        created_concept = create_concept(con, new_concept)
        con.commit()
    except Exception:
        con.rollback()
        raise

    return created_concept



@concept_router.patch("/{concept_id}")
def update_concept_endpoint(
    concept_id: int,
    concept_schema: ConceptUpdate,
    con: sqlite3.Connection = Depends(get_db)
) -> Concept:

    concept_to_update = get_concept_by_id(con, concept_id)

    if concept_to_update is None:
        raise HTTPException(404, "The concept does not exist")

    # Get the fields the user provided (as a dictionary)
    update_data = concept_schema.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(422, "At least one field must be provided for an update")

    for key, val in update_data.items():
        setattr(concept_to_update, key, val)

    try:
        update_concept(con, concept_to_update)
        con.commit()
    except Exception:
        con.rollback()
        raise

    return concept_to_update



@concept_router.delete("/{concept_id}", status_code=204)
def delete_concept_endpoint(
    concept_id: int,
    con: sqlite3.Connection = Depends(get_db)
) -> None:

    try:
        delete_concept(con, concept_id)
        con.commit()
    except NotFoundError as exception:
        con.rollback()
        raise HTTPException(404, detail=str(exception))
    except Exception:
        con.rollback()
        raise