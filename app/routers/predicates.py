from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_db
from app.exceptions import DuplicateError, NotFoundError
from app.models import Predicate
from app.repositories import(
    get_predicate_by_id,
    get_all_predicates,
)
from app.services import (
    create_predicate,
    update_predicate,
    delete_predicate
)
from app.schemas import PredicateCreate, PredicateUpdate
import sqlite3

predicate_router = APIRouter(prefix="/predicates", tags=["predicates"])

@predicate_router.get("/{predicate_id}")
def get_predicate_by_id_endpoint(
    predicate_id: int,
    con: sqlite3.Connection = Depends(get_db)
) -> Predicate:

    predicate = get_predicate_by_id(con, predicate_id)

    if predicate is None:
        raise HTTPException(404, "The predicate does not exist")

    return predicate



@predicate_router.get("/")
def get_all_predicates_endpoint(
    con: sqlite3.Connection = Depends(get_db)
) -> list[Predicate]:

    return get_all_predicates(con)



@predicate_router.post("/", status_code=201)
def create_predicate_endpoint(
    predicate_schema: PredicateCreate,
    con: sqlite3.Connection = Depends(get_db)
) -> Predicate:

    new_predicate = Predicate(name=predicate_schema.name, bidirectional=predicate_schema.bidirectional)

    try:
        created_predicate = create_predicate(con, new_predicate)
        con.commit()
    except DuplicateError as exception:
        con.rollback()
        raise HTTPException(409, detail=str(exception))
    except Exception:
        con.rollback()
        raise

    return created_predicate



@predicate_router.patch("/{predicate_id}")
def update_predicate_endpoint(
    predicate_id: int,
    predicate_schema: PredicateUpdate,
    con: sqlite3.Connection = Depends(get_db)
) -> Predicate:

    predicate_to_update = get_predicate_by_id(con, predicate_id)

    if predicate_to_update is None:
        raise HTTPException(404, "The predicate does not exist")

    update_data = predicate_schema.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(422, "At least one field must be provided for an update")

    for key, val in update_data.items():
        setattr(predicate_to_update, key, val)

    try:
        update_predicate(con, predicate_to_update)
        con.commit()
    except DuplicateError as exception:
        con.rollback()
        raise HTTPException(409, detail=str(exception))
    except Exception:
        con.rollback()
        raise

    return predicate_to_update



@predicate_router.delete("/{predicate_id}", status_code=204)
def delete_predicate_endpoint(
    predicate_id: int,
    con: sqlite3.Connection = Depends(get_db)
) -> None:

    try:
        delete_predicate(con, predicate_id)
        con.commit()
    except NotFoundError as exception:
        con.rollback()
        raise HTTPException(404, detail=str(exception))
    except Exception:
        con.rollback()
        raise