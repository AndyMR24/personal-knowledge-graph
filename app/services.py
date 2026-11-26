from app.exceptions import NotFoundError, DuplicateError
from app.models import Predicate, Relationship, ProjectConcept, GraphResult
from app.repositories import (
    get_concept_by_id,
    delete_concept as repositories_delete_concept,
    get_all_concepts,
    delete_relationships_for_concept,
    delete_project_concepts_for_concept,
    create_predicate as repositories_create_predicate,
    get_predicate_by_id,
    get_predicate_by_name,
    update_predicate as repositories_update_predicate,
    delete_predicate as repositories_delete_predicate,
    get_all_predicates,
    delete_relationships_for_predicate,
    get_relationship_by_id,
    create_relationship as repositories_create_relationship,
    update_relationship as repositories_update_relationship,
    delete_relationship as repositories_delete_relationship,
    get_all_relationships,
    get_project_by_id,
    delete_project as repositories_delete_project,
    delete_project_concepts_for_project,
    get_all_projects,
    create_project_concept as repositories_create_project_concept,
    get_project_concept_by_id,
    update_project_concept as repositories_update_project_concept,
    delete_project_concept as repositories_delete_project_concept,
    get_all_project_concepts
)
import sqlite3

def delete_concept(con: sqlite3.Connection, concept_id: int) -> bool:
    if get_concept_by_id(con, concept_id) is None:
        raise NotFoundError("The concept does not exist")

    # Create a save point in case an operation fails
    con.execute("SAVEPOINT delete_concept")

    try:
        delete_relationships_for_concept(con, concept_id)
        delete_project_concepts_for_concept(con, concept_id)

        concept_deleted = repositories_delete_concept(con, concept_id)

        if not concept_deleted:
            raise RuntimeError("An error happened and the concept did not get deleted")

        # Do not forget to release the save point!
        con.execute("RELEASE SAVEPOINT delete_concept")

        return concept_deleted
    except Exception:
        # Return to the save point
        con.execute("ROLLBACK TO SAVEPOINT delete_concept")
        # Do not forget to release the save point!
        con.execute("RELEASE SAVEPOINT delete_concept")
        # As well as re-raise the exception!
        raise



def get_concept_neighborhood(con: sqlite3.Connection, concept_id: int) -> GraphResult:
    table_concept = get_concept_by_id(con, concept_id)

    if table_concept is None:
        raise NotFoundError("The concept does not exist")

    res: GraphResult = {
        "concepts": [table_concept],
        "predicates": [],
        "relationships": [],
        "projects": [],
        "project_concepts": []
    }

    relationships = get_all_relationships(con)

    for r in relationships:
        if r.subject_id == concept_id:
            neighbor_concept = get_concept_by_id(con, r.object_id)
            predicate = get_predicate_by_id(con, r.predicate_id)

            if neighbor_concept is None:
                raise NotFoundError("The neighbor concept does not exist")
            
            if predicate is None:
                raise NotFoundError("The predicate does not exist")
            
            if neighbor_concept not in res["concepts"]:
                res["concepts"].append(neighbor_concept)
            
            if predicate not in res["predicates"]:
                res["predicates"].append(predicate)
            
            res["relationships"].append(r)
        elif r.object_id == concept_id:
            neighbor_concept = get_concept_by_id(con, r.subject_id)
            predicate = get_predicate_by_id(con, r.predicate_id)

            if neighbor_concept is None:
                raise NotFoundError("The neighbor concept does not exist")
            
            if predicate is None:
                raise NotFoundError("The predicate does not exist")
            
            if neighbor_concept not in res["concepts"]:
                res["concepts"].append(neighbor_concept)
            
            if predicate not in res["predicates"]:
                res["predicates"].append(predicate)
            
            res["relationships"].append(r)

    project_concepts = get_all_project_concepts(con)

    for pc in project_concepts:
        if pc.concept_id == concept_id:
            project = get_project_by_id(con, pc.project_id)

            if project is None:
                raise NotFoundError("The project does not exist")
            
            if table_concept is None:
                raise NotFoundError("The concept does not exist")

            if project not in res["projects"]:
                res["projects"].append(project)
            
            if table_concept not in res["concepts"]:
                res["concepts"].append(table_concept)

            res["project_concepts"].append(pc)

    return res



def create_predicate(con: sqlite3.Connection, predicate: Predicate) -> Predicate:
    if get_predicate_by_name(con, predicate.name) is not None:
        raise DuplicateError("This predicate already exsits")

    return repositories_create_predicate(con, predicate)



def update_predicate(con: sqlite3.Connection, predicate: Predicate) -> bool:
    if predicate.id is None or get_predicate_by_id(con, predicate.id) is None:
        raise NotFoundError("The predicate does not exist")

    possible_duplicate = get_predicate_by_name(con, predicate.name)

    if possible_duplicate is not None and possible_duplicate.id != predicate.id:
        raise DuplicateError("A predicate with this name already exists")

    return repositories_update_predicate(con, predicate)



def delete_predicate(con: sqlite3.Connection, predicate_id: int) -> bool:
    table_predicate = get_predicate_by_id(con, predicate_id)
    
    if table_predicate is None:
        raise NotFoundError("The predicate does not exist")

    con.execute("SAVEPOINT delete_predicate")

    try:
        delete_relationships_for_predicate(con, predicate_id)

        predicate_deleted = repositories_delete_predicate(con, predicate_id)

        if not predicate_deleted:
            raise RuntimeError("An error happened and the predicate did not get deleted")

        con.execute("RELEASE SAVEPOINT delete_predicate")

        return predicate_deleted
    except Exception:
        con.execute("ROLLBACK TO SAVEPOINT delete_predicate")
        con.execute("RELEASE SAVEPOINT delete_predicate")
        raise



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
            raise DuplicateError("This relationship already exists")
        elif relationship.subject_id == rel.object_id and relationship.object_id == rel.subject_id and relationship.predicate_id == rel.predicate_id and predicate.bidirectional:
            raise DuplicateError("This relationship already exists")

    return repositories_create_relationship(con, relationship)



def update_relationship(con: sqlite3.Connection, relationship: Relationship) -> bool:
    if relationship.id is None or get_relationship_by_id(con, relationship.id) is None:
        raise NotFoundError("The relationship does not exist")

    predicate = get_predicate_by_id(con, relationship.predicate_id)

    if get_concept_by_id(con, relationship.subject_id) is None:
        raise NotFoundError("The relationship has a missing subject_id")
    elif get_concept_by_id(con, relationship.object_id) is None:
        raise NotFoundError("The relationship has a missing object_id")
    elif predicate is None:
        raise NotFoundError("The relationship has a missing predicate_id")

    # Could be optimized in the future
    relationships = get_all_relationships(con)

    for rel in relationships:
        if rel.subject_id == relationship.subject_id and rel.predicate_id == relationship.predicate_id and rel.object_id == relationship.object_id and rel.id != relationship.id:
            raise DuplicateError("This relationship already exists")
        elif rel.subject_id == relationship.object_id and rel.predicate_id == relationship.predicate_id and rel.object_id == relationship.subject_id and rel.id != relationship.id and predicate.bidirectional:
            raise DuplicateError("This relationship already exists")

    return repositories_update_relationship(con, relationship)



def delete_relationship(con: sqlite3.Connection, relationship_id: int) -> bool:
    table_relationship = get_relationship_by_id(con, relationship_id)
    
    if table_relationship is None:
        raise NotFoundError("The relationship does not exist")

    return repositories_delete_relationship(con, relationship_id)



def delete_project(con: sqlite3.Connection, project_id: int) -> bool:
    table_project = get_project_by_id(con, project_id)
    
    if table_project is None:
        raise NotFoundError("The project does not exist")

    con.execute("SAVEPOINT delete_project")

    try:
        delete_project_concepts_for_project(con, project_id)

        project_deleted = repositories_delete_project(con, project_id)

        if not project_deleted:
            raise RuntimeError("An error happened and the project did not get deleted")

        con.execute("RELEASE SAVEPOINT delete_project")
        
        return project_deleted
    except Exception:
        con.execute("ROLLBACK TO SAVEPOINT delete_project")
        con.execute("RELEASE SAVEPOINT delete_project")
        raise



def create_project_concept(con: sqlite3.Connection, project_concept: ProjectConcept) -> ProjectConcept:
    if project_concept.concept_id is None or get_concept_by_id(con, project_concept.concept_id) is None:
        raise NotFoundError("The concept does not exist")
    elif project_concept.project_id is None or get_project_by_id(con, project_concept.project_id) is None:
        raise NotFoundError("The project does not exist")

    # Could be optimized in the future
    project_concepts = get_all_project_concepts(con)

    for pc in project_concepts:
        if pc.concept_id == project_concept.concept_id and pc.project_id == project_concept.project_id:
            raise DuplicateError("The concept is already associated with this project")

    return repositories_create_project_concept(con, ProjectConcept(project_concept.concept_id, project_concept.project_id))



# Currently unused, could be implemented in the future
def update_project_concept(con, project_concept: ProjectConcept) -> bool:
    if project_concept.id is None or get_project_concept_by_id(con, project_concept.id) is None:
        raise NotFoundError("The concept is not associated with this project")
    elif get_concept_by_id(con, project_concept.concept_id) is None:
        raise NotFoundError("The concept does not exist")
    elif get_project_by_id(con, project_concept.project_id) is None:
        raise NotFoundError("The project does not exist")

    return repositories_update_project_concept(con, project_concept)



def delete_project_concept(con: sqlite3.Connection, project_concept_id: int) -> bool:
    project_concept = get_project_concept_by_id(con, project_concept_id)
    
    if project_concept is None:
        raise NotFoundError("The concept is not associated with this project")
    elif get_concept_by_id(con, project_concept.concept_id) is None:
        raise NotFoundError("The concept does not exist")
    elif get_project_by_id(con, project_concept.project_id) is None:
        raise NotFoundError("The project does not exist")

    return repositories_delete_project_concept(con, project_concept_id)



def get_full_graph(con: sqlite3.Connection) -> GraphResult:
    return {
        "concepts": get_all_concepts(con),
        "predicates": get_all_predicates(con),
        "relationships": get_all_relationships(con),
        "projects": get_all_projects(con),
        "project_concepts": get_all_project_concepts(con)
    }