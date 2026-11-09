from app.database import get_connection, init_db
from app.models import Concept, Predicate, Relationship, Project, ProjectConcept
from app.repositories import create_concept, get_concept_by_id, update_concept, delete_concept, get_all_concepts, create_predicate, get_predicate_by_id, update_predicate, delete_predicate, get_all_predicates, create_relationship, get_relationship_by_id, update_relationship, delete_relationship, get_all_relationships, create_project, get_project_by_id, update_project, delete_project, get_all_projects, create_project_concept, get_project_concept_by_id, update_project_concept, delete_project_concept, get_all_project_concepts
import pytest
import sqlite3

@pytest.fixture
def con():
    # Create the connection
    con = get_connection(":memory:")
    
    try:
        init_db(con)
        # Give the connection to the test
        yield con
    finally:
        # Close the connection after the test finishes
        con.close()



@pytest.fixture
def concept():
    return Concept("Python", content = "Something Pythonic")



@pytest.fixture
def concept2():
    return Concept("Programming Language", content = "Easy")



@pytest.fixture
def predicate():
    return Predicate(name = "isA", bidirectional = False)



@pytest.fixture
def relationship(con, concept, concept2, predicate):
    rel_subject = create_concept(con, concept)
    rel_object = create_concept(con, concept2)
    rel_predicate = create_predicate(con, predicate)
    
    return Relationship(rel_subject.id, rel_predicate.id, rel_object.id)



def test_create_concept(con, concept):
    table_concept = create_concept(con, concept)

    res = con.execute("SELECT * FROM concepts WHERE id = ?;", (table_concept.id,)).fetchone()

    assert res is not None
    assert res[0] == table_concept.id
    assert res[1] == table_concept.title
    assert res[2] == table_concept.content
    


def test_get_concept_by_id(con, concept):
    table_concept = create_concept(con, concept)

    res = get_concept_by_id(con, table_concept.id)

    assert res is not None
    assert res.id == table_concept.id
    assert res.title == table_concept.title
    assert res.content == table_concept.content



def test_get_invalid_concept_by_id(con):
    assert get_concept_by_id(con, 1) is None



def test_update_concept(con, concept):
    table_concept = create_concept(con, concept)

    concept2 = Concept("Java", table_concept.id, "Something Java-like")

    assert update_concept(con, concept2)

    updated_concept = get_concept_by_id(con, table_concept.id)

    assert updated_concept is not None
    assert updated_concept.id == table_concept.id
    assert updated_concept.title == concept2.title
    assert updated_concept.content == concept2.content



def test_update_concept_with_nonexistent_id(con):
    assert not update_concept(con, Concept("Python", 1, "Something Pythonic"))



def test_update_concept_with_missing_id(con):
    assert not update_concept(con, Concept("Python"))



def test_delete_concept(con, concept):
    table_concept = create_concept(con, concept)

    assert delete_concept(con, table_concept.id)
    assert get_concept_by_id(con, table_concept.id) is None



def test_delete_nonexistent_concept(con):
    assert not delete_concept(con, 1)



def test_get_all_concepts(con, concept):
    concept2 = Concept("Java", 2, "Something Java-like")

    table_concept1 = create_concept(con, concept)
    table_concept2 = create_concept(con, concept2)

    assert get_all_concepts(con) == [get_concept_by_id(con, table_concept1.id), get_concept_by_id(con, table_concept2.id)]



def test_get_all_concepts_with_empty_database(con):
    assert get_all_concepts(con) == []



def test_create_predicate(con, predicate):
    table_predicate = create_predicate(con, predicate)

    res = con.execute("SELECT * FROM predicates;").fetchone()

    assert res is not None
    assert res[0] == table_predicate.id
    assert res[1] == table_predicate.name
    assert res[2] == table_predicate.bidirectional



def test_get_predicate_by_id(con, predicate):
    table_predicate = create_predicate(con, predicate)

    res = get_predicate_by_id(con, table_predicate.id)

    assert res is not None
    assert res.id == table_predicate.id
    assert res.name == table_predicate.name
    assert res.bidirectional == table_predicate.bidirectional



def test_get_invalid_predicate_by_id(con):
    assert get_predicate_by_id(con, 1) is None



def test_update_predicate(con, predicate):
    table_predicate = create_predicate(con, predicate)

    predicate2 = Predicate(table_predicate.id, "uses")

    assert update_predicate(con, predicate2)

    updated_predicate = get_predicate_by_id(con, table_predicate.id)

    assert updated_predicate is not None
    assert updated_predicate.id == table_predicate.id
    assert updated_predicate.name == predicate2.name
    assert updated_predicate.bidirectional == predicate2.bidirectional



def test_update_predicate_with_nonexistent_id(con):
    assert not update_predicate(con, Predicate(1, "isA", False))



def test_update_predicate_with_missing_id(con):
    assert not update_predicate(con, Predicate(name = "isA"))



def test_delete_predicate(con, predicate):
    table_predicate = create_predicate(con, predicate)

    assert delete_predicate(con, table_predicate.id)
    assert get_predicate_by_id(con, table_predicate.id) is None



def test_delete_nonexistent_predicate(con):
    assert not delete_predicate(con, 1)



def test_get_all_predicates(con, predicate):
    predicate2 = Predicate(2, "uses")

    table_predicate1 = create_predicate(con, predicate)
    table_predicate2 = create_predicate(con, predicate2)

    assert get_all_predicates(con) == [get_predicate_by_id(con, table_predicate1.id), get_predicate_by_id(con, table_predicate2.id)]



def test_get_all_predicates_with_empty_database(con):
    assert get_all_predicates(con) == []



def test_create_relationship(con, relationship):
    table_relationship = create_relationship(con, relationship)

    res = con.execute("SELECT * FROM relationships;").fetchone()

    assert res is not None
    assert res[0] == table_relationship.id
    assert res[1] == table_relationship.subject_id
    assert res[2] == table_relationship.predicate_id
    assert res[3] == table_relationship.object_id



def test_create_relationship_with_foreign_keys(con, concept, concept2, predicate):
    table_concept1 = create_concept(con, concept)
    table_concept2 = create_concept(con, concept2)
    table_predicate = create_predicate(con, predicate)

    with pytest.raises(sqlite3.IntegrityError):
        create_relationship(con, Relationship(table_concept1.id, table_predicate.id, 999))

    with pytest.raises(sqlite3.IntegrityError):
        create_relationship(con, Relationship(999, table_predicate.id, table_concept1.id))

    with pytest.raises(sqlite3.IntegrityError):
        create_relationship(con, Relationship(table_concept1.id, 999, table_concept2.id))



def test_get_relationship_by_id(con, relationship):
    table_relationship = create_relationship(con, relationship)

    res = get_relationship_by_id(con, table_relationship.id)

    assert res is not None
    assert res.id == table_relationship.id
    assert res.subject_id == table_relationship.subject_id
    assert res.predicate_id == table_relationship.predicate_id
    assert res.object_id == table_relationship.object_id



def test_get_invalid_relationship_by_id(con):
    assert get_relationship_by_id(con, 1) is None



def test_update_relationship(con, relationship):
    table_relationship = create_relationship(con, relationship)
    concept3 = create_concept(con, Concept("C++", content = "Something Complicated"))

    relationship2 = Relationship(concept3.id, table_relationship.predicate_id, table_relationship.object_id, table_relationship.id)

    assert update_relationship(con, relationship2)

    updated_relationship = get_relationship_by_id(con, table_relationship.id)

    assert updated_relationship is not None
    assert updated_relationship.id == table_relationship.id
    assert updated_relationship.subject_id == relationship2.subject_id
    assert updated_relationship.predicate_id == table_relationship.predicate_id
    assert updated_relationship.object_id == table_relationship.object_id



def test_update_relationship_with_nonexistent_id(con):
    assert not update_relationship(con, Relationship(1, 1, 2, 999))



def test_update_relationship_with_missing_id(con):
    assert not update_relationship(con, Relationship(1, 1, 2))



def test_delete_relationship(con, relationship):
    table_relationship = create_relationship(con, relationship)

    assert delete_relationship(con, table_relationship.id)
    assert get_relationship_by_id(con, table_relationship.id) is None



def test_delete_nonexistent_relationship(con):
    assert not delete_relationship(con, 1)



def test_delete_referenced_concept(con, relationship):
    table_relationship = create_relationship(con, relationship)

    with pytest.raises(sqlite3.IntegrityError):
        delete_concept(con, table_relationship.subject_id)

    with pytest.raises(sqlite3.IntegrityError):
        delete_concept(con, table_relationship.object_id)



def test_delete_referenced_predicate(con, relationship):
    table_relationship = create_relationship(con, relationship)

    with pytest.raises(sqlite3.IntegrityError):
        delete_predicate(con, table_relationship.predicate_id)



def test_get_all_relationships(con, relationship):
    concept3 = create_concept(con, Concept("C++", content = "Something Complicated"))

    table_relationship1 = create_relationship(con, relationship)
    table_relationship2 = create_relationship(con, Relationship(concept3.id, table_relationship1.predicate_id, table_relationship1.object_id))

    assert get_all_relationships(con) == [get_relationship_by_id(con, table_relationship1.id), get_relationship_by_id(con, table_relationship2.id)]



def test_get_all_relationships_with_empty_database(con):
    assert get_all_relationships(con) == []



def test_create_project(con):
    table_project = create_project(con, Project("Thesis", description = "My thesis"))

    res = con.execute("SELECT * FROM projects WHERE id = ?;", (table_project.id,)).fetchone()

    assert table_project.id is not None
    assert res is not None
    assert res[0] == table_project.id
    assert res[1] == table_project.title
    assert res[2] == table_project.description



def test_get_project_by_id(con):
    table_project = create_project(con, Project("Thesis", description = "My thesis"))

    res = get_project_by_id(con, table_project.id)

    assert res is not None
    assert res.id == table_project.id
    assert res.title == table_project.title
    assert res.description == table_project.description



def test_get_invalid_project_by_id(con):
    assert get_project_by_id(con, 1) is None



def test_update_project(con):
    table_project = create_project(con, Project("Thesis", description = "My thesis"))

    project2 = Project("Dissertation", table_project.id, "My dissertation")

    assert update_project(con, project2)

    updated_project = get_project_by_id(con, table_project.id)

    assert updated_project is not None
    assert updated_project.id == table_project.id
    assert updated_project.title == project2.title
    assert updated_project.description == project2.description



def test_update_project_with_nonexistent_id(con):
    assert not update_project(con, Project("Thesis", 1, "My thesis"))



def test_update_project_with_missing_id(con):
    assert not update_project(con, Project("Thesis"))



def test_delete_project(con):
    table_project = create_project(con, Project("Thesis"))

    assert delete_project(con, table_project.id)
    assert get_project_by_id(con, table_project.id) is None



def test_delete_nonexistent_project(con):
    assert not delete_project(con, 1)



def test_get_all_projects(con):
    table_project1 = create_project(con, Project("Thesis", description = "My thesis"))
    table_project2 = create_project(con, Project("Portfolio"))

    assert get_all_projects(con) == [
        get_project_by_id(con, table_project1.id),
        get_project_by_id(con, table_project2.id)
    ]



def test_get_all_projects_with_empty_database(con):
    assert get_all_projects(con) == []



def test_create_project_concept(con):
    table_concept = create_concept(con, Concept("Python"))
    table_project = create_project(con, Project("Thesis"))

    table_project_concept = create_project_concept(con, ProjectConcept(table_concept.id, table_project.id))

    res = con.execute(
        "SELECT * FROM project_concepts WHERE id = ?;",
        (table_project_concept.id,)
    ).fetchone()

    assert table_project_concept.id is not None
    assert res is not None
    assert res[0] == table_project_concept.id
    assert res[1] == table_project_concept.concept_id
    assert res[2] == table_project_concept.project_id



def test_get_project_concept_by_id(con):
    table_concept = create_concept(con, Concept("Python"))
    table_project = create_project(con, Project("Thesis"))
    table_project_concept = create_project_concept(con, ProjectConcept(table_concept.id, table_project.id))

    res = get_project_concept_by_id(con, table_project_concept.id)

    assert res is not None
    assert res.id == table_project_concept.id
    assert res.concept_id == table_project_concept.concept_id
    assert res.project_id == table_project_concept.project_id



def test_get_invalid_project_concept_by_id(con):
    assert get_project_concept_by_id(con, 1) is None



def test_update_project_concept(con):
    table_concept1 = create_concept(con, Concept("Python"))
    table_concept2 = create_concept(con, Concept("Testing"))
    table_project1 = create_project(con, Project("Thesis"))
    table_project2 = create_project(con, Project("Portfolio"))
    table_project_concept = create_project_concept(con, ProjectConcept(table_concept1.id, table_project1.id)
    )

    project_concept2 = ProjectConcept(
        table_concept2.id,
        table_project2.id,
        table_project_concept.id
    )

    assert update_project_concept(con, project_concept2)

    updated_project_concept = get_project_concept_by_id(con, table_project_concept.id)

    assert updated_project_concept is not None
    assert updated_project_concept.id == table_project_concept.id
    assert updated_project_concept.concept_id == project_concept2.concept_id
    assert updated_project_concept.project_id == project_concept2.project_id



def test_update_project_concept_with_nonexistent_id(con):
    table_concept = create_concept(con, Concept("Python"))
    table_project = create_project(con, Project("Thesis"))

    assert not update_project_concept(con, ProjectConcept(table_concept.id, table_project.id, 999))



def test_update_project_concept_with_missing_id(con):
    assert not update_project_concept(con, ProjectConcept(1, 1))



def test_delete_project_concept(con):
    table_concept = create_concept(con, Concept("Python"))
    table_project = create_project(con, Project("Thesis"))
    table_project_concept = create_project_concept(con, ProjectConcept(table_concept.id, table_project.id))

    assert delete_project_concept(con, table_project_concept.id)
    assert get_project_concept_by_id(con, table_project_concept.id) is None



def test_delete_nonexistent_project_concept(con):
    assert not delete_project_concept(con, 1)



def test_get_all_project_concepts(con):
    table_concept1 = create_concept(con, Concept("Python"))
    table_concept2 = create_concept(con, Concept("Testing"))
    table_project = create_project(con, Project("Thesis"))
    table_project_concept1 = create_project_concept(con, ProjectConcept(table_concept1.id, table_project.id))
    table_project_concept2 = create_project_concept(con, ProjectConcept(table_concept2.id, table_project.id))

    assert get_all_project_concepts(con) == [
        get_project_concept_by_id(con, table_project_concept1.id),
        get_project_concept_by_id(con, table_project_concept2.id)
    ]



def test_get_all_project_concepts_with_empty_database(con):
    assert get_all_project_concepts(con) == []



def test_create_project_concept_with_nonexistent_concept_id(con):
    table_project = create_project(con, Project("Thesis"))

    with pytest.raises(sqlite3.IntegrityError):
        create_project_concept(con, ProjectConcept(999, table_project.id))



def test_create_project_concept_with_nonexistent_project_id(con):
    table_concept = create_concept(con, Concept("Python"))

    with pytest.raises(sqlite3.IntegrityError):
        create_project_concept(con, ProjectConcept(table_concept.id, 999))



def test_create_duplicate_project_concept(con):
    table_concept = create_concept(con, Concept("Python"))
    table_project = create_project(con, Project("Thesis"))
    create_project_concept(con, ProjectConcept(table_concept.id, table_project.id))

    with pytest.raises(sqlite3.IntegrityError):
        create_project_concept(con, ProjectConcept(table_concept.id, table_project.id))



def test_delete_project_with_project_concepts(con):
    table_concept = create_concept(con, Concept("Python"))
    table_project = create_project(con, Project("Thesis"))
    create_project_concept(con, ProjectConcept(table_concept.id, table_project.id))

    with pytest.raises(sqlite3.IntegrityError):
        delete_project(con, table_project.id)



def test_delete_concept_with_project_concepts(con):
    table_concept = create_concept(con, Concept("Python"))
    table_project = create_project(con, Project("Thesis"))
    create_project_concept(con, ProjectConcept(table_concept.id, table_project.id))

    with pytest.raises(sqlite3.IntegrityError):
        delete_concept(con, table_concept.id)