from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_db
from app.exceptions import DuplicateError, NotFoundError
from app.models import Relationship
from app.repositories import (
    get_relationship_by_id,
    get_all_relationships
)
from app.services import create_relationship, update_relationship, delete_relationship
from app.schemas import RelationshipCreate, RelationshipUpdate
import sqlite3

relationship_router = APIRouter(prefix="/relationships", tags=["relationships"])

@relationship_router.get("/{relationship_id}")
def get_relationship_by_id_endpoint(
    relationship_id: int,
    con: sqlite3.Connection = Depends(get_db)
) -> Relationship:

    relationship = get_relationship_by_id(con, relationship_id)

    if relationship is None:
        raise HTTPException(404, "The relationship does not exist")

    return relationship



@relationship_router.get("/")
def get_all_relationships_endpoint(
    con: sqlite3.Connection = Depends(get_db)
) -> list[Relationship]:

    return get_all_relationships(con)



@relationship_router.post("/", status_code=201)
def create_relationship_endpoint(
    relationship_schema: RelationshipCreate,
    con: sqlite3.Connection = Depends(get_db)
) -> Relationship:

    new_relationship = Relationship(
        subject_id=relationship_schema.subject_id,
        predicate_id=relationship_schema.predicate_id,
        object_id=relationship_schema.object_id
    )

    try:
        created_relationship = create_relationship(con, new_relationship)
        con.commit()
    except DuplicateError as exception:
        con.rollback()
        raise HTTPException(409, detail=str(exception))
    except Exception:
        con.rollback()
        raise

    return created_relationship



@relationship_router.patch("/{relationship_id}")
def update_relationship_endpoint(
    relationship_id: int,
    relationship_schema: RelationshipUpdate,
    con: sqlite3.Connection = Depends(get_db)
) -> Relationship:

    relationship_to_update = get_relationship_by_id(con, relationship_id)

    if relationship_to_update is None:
        raise HTTPException(404, "The relationship does not exist")

    update_data = relationship_schema.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(422, "At least one field must be provided for an update")

    for key, val in update_data.items():
        setattr(relationship_to_update, key, val)

    try:
        update_relationship(con, relationship_to_update)
        con.commit()
    except DuplicateError as exception:
        con.rollback()
        raise HTTPException(409, detail=str(exception))
    except NotFoundError as exception:
        con.rollback()
        raise HTTPException(404, detail=str(exception))
    except Exception:
        con.rollback()
        raise

    return relationship_to_update



@relationship_router.delete("/{relationship_id}", status_code=204)
def delete_relationship_endpoint(
    relationship_id: int,
    con: sqlite3.Connection = Depends(get_db)
) -> None:

    try:
        delete_relationship(con, relationship_id)
        con.commit()
    except NotFoundError as exception:
        con.rollback()
        raise HTTPException(404, detail=str(exception))
    except Exception:
        con.rollback()
        raise