from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_db
from app.exceptions import NotFoundError
from app.models import Project
from app.repositories import (
    create_project,
    get_project_by_id,
    update_project,
    get_all_projects,
    search_projects_by_title
)
from app.services import delete_project
from app.schemas import ProjectCreate, ProjectUpdate
import sqlite3

project_router = APIRouter(prefix="/projects", tags=["projects"])

@project_router.get("/{project_id}")
def get_project_by_id_endpoint(
    project_id: int,
    con: sqlite3.Connection = Depends(get_db)
) -> Project:
    
    project = get_project_by_id(con, project_id)

    if project is None:
        raise HTTPException(404, "The project does not exist")

    return project



@project_router.get("/")
def get_all_projects_endpoint(
    title: str | None = None,
    con: sqlite3.Connection = Depends(get_db)
) -> list[Project]:
    
    return get_all_projects(con) if title is None else search_projects_by_title(con, title)



@project_router.post("/", status_code=201)
def create_project_endpoint(
    project_schema: ProjectCreate,
    con: sqlite3.Connection = Depends(get_db)
) -> Project:
    
    new_project = Project(title=project_schema.title, description=project_schema.description)

    try:
        created_project = create_project(con, new_project)
        con.commit()
    except Exception:
        con.rollback()
        raise

    return created_project



@project_router.patch("/{project_id}")
def update_project_endpoint(
    project_id: int,
    project_schema: ProjectUpdate,
    con: sqlite3.Connection = Depends(get_db)
) -> Project:

    project_to_update = get_project_by_id(con, project_id)

    if project_to_update is None:
        raise HTTPException(404, "The project does not exist")

    update_data = project_schema.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(422, "At least one field must be provided for an update")

    for key, val in update_data.items():
        setattr(project_to_update, key, val)

    try:
        update_project(con, project_to_update)
        con.commit()
    except Exception:
        con.rollback()
        raise

    return project_to_update



@project_router.delete("/{project_id}", status_code=204)
def delete_project_endpoint(
    project_id: int,
    con: sqlite3.Connection = Depends(get_db)
) -> None:

    try:
        delete_project(con, project_id)
        con.commit()
    except NotFoundError as exception:
        con.rollback()
        raise HTTPException(404, detail=str(exception))
    except Exception:
        con.rollback()
        raise