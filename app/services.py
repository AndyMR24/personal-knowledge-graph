from app.exceptions import NotFoundError, DuplicateError
from app.models import Concept, Relationship, ProjectConcept
from app.repositories import (
    get_concept_by_id,
    delete_concept as repositories_delete_concept,
    get_all_concepts,
    get_predicate_by_id,
    create_relationship as repositories_create_relationship,
    get_all_relationships,
    get_project_by_id,
    get_all_project_concepts,
    create_project_concept as repositories_create_project_concept,
    get_project_concept_by_id,
    delete_project_concept,
    delete_relationships_for_concept,
    delete_project_concepts_for_concept)
import sqlite3

def create_relationship(con: sqlite3.Connection, relationship: Relationship) -> Relationship:
    predicate = get_predicate_by_id(con, relationship.predicate_id)

    if not get_concept_by_id(con, relationship.subject_id):
        raise NotFoundError("The subject does not exist")
    elif not predicate:
        raise NotFoundError("The predicate does not exist")
    elif not get_concept_by_id(con, relationship.object_id):
        raise NotFoundError("The object does not exist")

    # Could be optimized in the future
    relationships = get_all_relationships(con)

    for rel in relationships:
        if relationship.subject_id == rel.subject_id and relationship.predicate_id == rel.predicate_id and relationship.object_id == rel.object_id:
            raise DuplicateError("This is a duplicated relationship")
        elif relationship.subject_id == rel.object_id and relationship.object_id == rel.subject_id and relationship.predicate_id == rel.predicate_id:
            if predicate.bidirectional:
                raise DuplicateError("This relationship already exists")

    return repositories_create_relationship(con, relationship)



def delete_concept(con: sqlite3.Connection, concept_id: int) -> bool:
    if get_concept_by_id(con, concept_id) is None:
        raise NotFoundError("The concept does not exist")

    con.execute("SAVEPOINT delete_concept")

    try:
        delete_relationships_for_concept(con, concept_id)
        delete_project_concepts_for_concept(con, concept_id)

        concept_deleted = repositories_delete_concept(con, concept_id)

        if not concept_deleted:
            raise RuntimeError("An error happened and the concept did not get deleted")

        con.execute("RELEASE SAVEPOINT delete_concept")

        return concept_deleted
    except Exception:
        con.execute("ROLLBACK TO SAVEPOINT delete_concept")
        con.execute("RELEASE SAVEPOINT delete_concept")
        raise



def add_concept_to_project(con: sqlite3.Connection, concept_id: int, project_id: int) -> ProjectConcept:
    if concept_id is None or get_concept_by_id(con, concept_id) is None:
        raise NotFoundError("The concept does not exist")

    if project_id is None or get_project_by_id(con, project_id) is None:
        raise NotFoundError("The project does not exist")

    # Could be optimized in the future
    project_concepts = get_all_project_concepts(con)

    for pc in project_concepts:
        if pc.concept_id == concept_id and pc.project_id == project_id:
            raise DuplicateError("This concept is already associated with this project")

    return repositories_create_project_concept(con, ProjectConcept(concept_id, project_id))



def remove_concept_from_project(con: sqlite3.Connection, project_concept: ProjectConcept) -> bool:
    if project_concept.id is None or get_project_concept_by_id(con, project_concept.id) is None:
        raise NotFoundError("The concept is not associated with this project")

    return delete_project_concept(con, project_concept.id)



def get_full_graph(con: sqlite3.Connection) -> tuple[list[Concept], list[Relationship]]:
    return (get_all_concepts(con), get_all_relationships(con))



def get_concept_neighborhood(con: sqlite3.Connection, concept_id: int) -> tuple[list[Concept], list[Relationship]]:
    table_concept = get_concept_by_id(con, concept_id)

    if table_concept is None:
        raise NotFoundError("The concept does not exist")

    relationships = get_all_relationships(con)

    neighbor_concepts = [table_concept]
    neighbor_relationships = []

    for r in relationships:
        if r.subject_id == concept_id:
            neighbor_concept = get_concept_by_id(con, r.object_id)

            if neighbor_concept is None:
                raise NotFoundError("The neighbor concept does not exist")
            
            if neighbor_concept not in neighbor_concepts:
                neighbor_concepts.append(neighbor_concept)
            
            neighbor_relationships.append(r)
        elif r.object_id == concept_id:
            neighbor_concept = get_concept_by_id(con, r.subject_id)

            if neighbor_concept is None:
                raise NotFoundError("The neighbor concept does not exist")
            
            if neighbor_concept not in neighbor_concepts:
                neighbor_concepts.append(neighbor_concept)
            
            neighbor_relationships.append(r)

    return (neighbor_concepts, neighbor_relationships)