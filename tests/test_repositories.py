from app.database import get_connection, init_db
from app.models import Concept, Predicate, Relationship, Project, ProjectConcept
from app.repositories import (
    create_concept,
    get_concept_by_id,
    update_concept,
    delete_concept,
    get_all_concepts,
    search_concepts_by_title,
    delete_relationships_for_concept, delete_project_concepts_for_concept,
    create_predicate,
    get_predicate_by_id,
    get_predicate_by_name,
    update_predicate,
    delete_predicate,
    get_all_predicates,
    delete_relationships_for_predicate,
    create_relationship,
    get_relationship_by_id,
    update_relationship,
    delete_relationship,
    get_all_relationships,
    create_project,
    get_project_by_id,
    update_project,
    delete_project,
    delete_project_concepts_for_project,
    get_all_projects,
    search_projects_by_title,
    create_project_concept,
    get_project_concept_by_id,
    update_project_concept,
    delete_project_concept,
    get_all_project_concepts)
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
def concept1(con):
    return create_concept(con, Concept("Python", content = "Something Pythonic"))

@pytest.fixture
def concept2(con):
    return create_concept(con, Concept("Programming Language", content = "Easy"))

@pytest.fixture
def concept3(con):
    return create_concept(con, Concept("Java", content = "Something Java-like"))

@pytest.fixture
def predicate1(con):
    return create_predicate(con, Predicate(name = "isA", bidirectional = False))

@pytest.fixture
def predicate2(con):
    return create_predicate(con, Predicate())

@pytest.fixture
def relationship1(con, concept1, concept2, predicate1):    
    return create_relationship(con, Relationship(concept1.id, predicate1.id, concept2.id))

@pytest.fixture
def relationship2(con, concept3, concept2, predicate1):
    return create_relationship(con, Relationship(concept3.id, predicate1.id, concept2.id))

@pytest.fixture
def relationship3(con, concept1, concept2, predicate2):
    return create_relationship(con, Relationship(concept1.id, predicate2.id, concept2.id))

@pytest.fixture
def self_relationship(con, concept1, predicate1):
    return create_relationship(con, Relationship(concept1.id, predicate1.id, concept1.id))

@pytest.fixture
def project1(con):
    return create_project(con, Project("Thesis", description = "My Thesis"))

@pytest.fixture
def project2(con):
    return create_project(con, Project("Personal Knowledge Graph", description = "My First Full Python Project"))

@pytest.fixture
def project3(con):
    return create_project(con, Project("Company Knowledge Graph", description = "A company's knowledge graph"))

@pytest.fixture
def project_concept1(con, concept1, project1):
    return create_project_concept(con, ProjectConcept(concept1.id, project1.id))

@pytest.fixture
def project_concept2(con, concept1, project2):
    return create_project_concept(con, ProjectConcept(concept1.id, project2.id))

@pytest.fixture
def project_concept3(con, concept2, project1):
    return create_project_concept(con, ProjectConcept(concept2.id, project1.id))



def test_create_concept(con, concept1):
    res = con.execute("SELECT * FROM concepts WHERE id = ?;", (concept1.id,)).fetchone()

    assert res is not None
    assert res[0] == concept1.id
    assert res[1] == concept1.title
    assert res[2] == concept1.content



def test_get_concept_by_id(con, concept1):
    res = get_concept_by_id(con, concept1.id)

    assert res is not None
    assert res.id == concept1.id
    assert res.title == concept1.title
    assert res.content == concept1.content



def test_get_invalid_concept_by_id(con):
    assert get_concept_by_id(con, 1) is None



def test_update_concept(con, concept1):
    concept2 = Concept("Java", concept1.id, "Something Java-like")

    assert update_concept(con, concept2)
    assert concept1.id is not None

    updated_concept = get_concept_by_id(con, concept1.id)

    assert updated_concept is not None
    assert updated_concept.id == concept1.id
    assert updated_concept.title == concept2.title
    assert updated_concept.content == concept2.content



def test_update_concept_with_nonexistent_id(con):
    assert not update_concept(con, Concept("Python", 1, "Something Pythonic"))



def test_update_concept_with_missing_id(con):
    assert not update_concept(con, Concept("Python"))



def test_delete_concept(con, concept1):
    assert delete_concept(con, concept1.id)
    assert get_concept_by_id(con, concept1.id) is None



def test_delete_nonexistent_concept(con):
    assert not delete_concept(con, 1)



def test_get_all_concepts(con, concept1):
    concept2 = Concept("Java", 2, "Something Java-like")

    table_concept2 = create_concept(con, concept2)

    assert table_concept2.id is not None

    assert get_all_concepts(con) == [get_concept_by_id(con, concept1.id), get_concept_by_id(con, table_concept2.id)]



@pytest.mark.parametrize("query, expected_titles", [
    ("Python", ["Python", "Python Testing", "Learning Python"]),
    ("python", ["Python", "Python Testing", "Learning Python"]),
    ("thon", ["Python", "Python Testing", "Learning Python"]),
    ("Java", []),
    ("", ["Python", "Python Testing", "Learning Python"])
])

def test_search_concepts_by_title(con, query, expected_titles):
    create_concept(con, Concept("Python"))
    create_concept(con, Concept("Python Testing"))
    create_concept(con, Concept("Learning Python"))

    concepts = search_concepts_by_title(con, query)

    assert sorted([concept.title for concept in concepts]) == sorted(expected_titles)



def test_get_all_concepts_with_empty_database(con):
    assert get_all_concepts(con) == []



def test_delete_relationships_for_concept_as_subject(con, relationship1):
    assert delete_relationships_for_concept(con, relationship1.subject_id) == 1
    assert get_relationship_by_id(con, relationship1.id) is None



def test_delete_relationships_for_concept_as_object(con, relationship1):
    assert delete_relationships_for_concept(con, relationship1.object_id) == 1
    assert get_relationship_by_id(con, relationship1.id) is None



def test_delete_relationships_without_mathing_concept(con):
    assert delete_relationships_for_concept(con, 999) == 0



def test_delete_multiple_relationships_for_concept(con, relationship1, relationship2):
    assert delete_relationships_for_concept(con, relationship1.object_id) == 2



def test_preserve_unrelated_relationships_for_concept(con, relationship1, relationship2):
    assert delete_relationships_for_concept(con, relationship1.subject_id) == 1
    assert get_relationship_by_id(con, relationship2.id) is not None



def test_delete_relationships_for_concept_without_associated_relationships(con, concept1):
    assert delete_relationships_for_concept(con, concept1.id) == 0



def test_delete_self_relationship_for_concept(con, self_relationship):
    assert delete_relationships_for_concept(con, self_relationship.subject_id) == 1
    assert get_relationship_by_id(con, self_relationship.id) is None



def test_delete_one_project_concept_association(con, concept1, project_concept1):
    assert delete_project_concepts_for_concept(con, concept1.id) == 1
    assert get_project_concept_by_id(con, project_concept1.id) is None



def test_delete_multiple_project_concept_associations(con, concept1, project_concept1, project_concept2):
    assert delete_project_concepts_for_concept(con, concept1.id) == 2
    assert get_project_concept_by_id(con, project_concept1.id) is None
    assert get_project_concept_by_id(con, project_concept2.id) is None



def test_delete_projects_for_concept_without_associated_projects(con, concept1):
    assert delete_project_concepts_for_concept(con, concept1.id) == 0



def test_preserve_unrelated_project_concepts(con, concept2, project_concept1, project_concept3):
    assert delete_project_concepts_for_concept(con, concept2.id) == 1
    assert get_project_concept_by_id(con, project_concept3.id) is None
    assert get_project_concept_by_id(con, project_concept1.id) == project_concept1



def test_create_predicate(con, predicate1):
    res = con.execute("SELECT * FROM predicates;").fetchone()

    assert res is not None
    assert res[0] == predicate1.id
    assert res[1] == predicate1.name
    assert res[2] == predicate1.bidirectional



def test_get_predicate_by_id(con, predicate1):
    res = get_predicate_by_id(con, predicate1.id)

    assert res is not None
    assert res.id == predicate1.id
    assert res.name == predicate1.name
    assert res.bidirectional == predicate1.bidirectional



def test_get_invalid_predicate_by_id(con):
    assert get_predicate_by_id(con, 1) is None



def test_get_predicate_by_name(con, predicate1):
    table_predicate1 =  get_predicate_by_name(con, predicate1.name)

    assert table_predicate1 is not None
    assert table_predicate1.name == predicate1.name
    assert table_predicate1.bidirectional == predicate1.bidirectional

    assert get_predicate_by_name(con) is None

    predicate2 = create_predicate(con, Predicate())
    table_predicate2 =  get_predicate_by_name(con)
    
    assert table_predicate2 is not None
    assert table_predicate2.name == predicate2.name
    assert table_predicate2.bidirectional == predicate2.bidirectional

    assert get_predicate_by_name(con, "Java") is None



def test_update_predicate(con, predicate1):
    predicate2 = Predicate(predicate1.id, "uses")

    assert update_predicate(con, predicate2)

    updated_predicate = get_predicate_by_id(con, predicate1.id)

    assert updated_predicate is not None
    assert updated_predicate.id == predicate1.id
    assert updated_predicate.name == predicate2.name
    assert updated_predicate.bidirectional == predicate2.bidirectional



def test_update_predicate_with_nonexistent_id(con):
    assert not update_predicate(con, Predicate(1, "isA", False))



def test_update_predicate_with_missing_id(con):
    assert not update_predicate(con, Predicate(name = "isA"))



def test_delete_predicate(con, predicate1):
    assert delete_predicate(con, predicate1.id)
    assert get_predicate_by_id(con, predicate1.id) is None



def test_delete_nonexistent_predicate(con):
    assert not delete_predicate(con, 1)



def test_get_all_predicates(con, predicate1):
    predicate2 = Predicate(2, "uses")

    table_predicate2 = create_predicate(con, predicate2)

    assert table_predicate2.id is not None

    assert get_all_predicates(con) == [get_predicate_by_id(con, predicate1.id), get_predicate_by_id(con, table_predicate2.id)]



def test_get_all_predicates_with_empty_database(con):
    assert get_all_predicates(con) == []



def test_delete_relationships_for_predicate(con, relationship1):
    assert delete_relationships_for_predicate(con, relationship1.predicate_id) == 1
    assert get_relationship_by_id(con, relationship1.id) is None



def test_delete_relationships_without_mathing_predicate(con):
    assert delete_relationships_for_predicate(con, 999) == 0



def test_delete_multiple_relationships_for_predicate(con, relationship1, relationship2):
    assert delete_relationships_for_predicate(con, relationship1.predicate_id) == 2



def test_preserve_unrelated_relationships_for_predicate(con, relationship1, relationship3):
    assert delete_relationships_for_predicate(con, relationship1.predicate_id) == 1
    assert get_relationship_by_id(con, relationship3.id) is not None



def test_delete_relationships_for_predicate_without_associated_relationships(con, predicate1):
    assert delete_relationships_for_predicate(con, predicate1.id) == 0



def test_delete_self_relationship_for_predicate(con, self_relationship):
    assert delete_relationships_for_predicate(con, self_relationship.predicate_id) == 1
    assert get_relationship_by_id(con, self_relationship.id) is None



def test_create_relationship(con, relationship1):
    res = con.execute("SELECT * FROM relationships;").fetchone()

    assert res is not None
    assert res[0] == relationship1.id
    assert res[1] == relationship1.subject_id
    assert res[2] == relationship1.predicate_id
    assert res[3] == relationship1.object_id



def test_create_relationship_with_foreign_keys(con, concept1, concept2, predicate1):
    with pytest.raises(sqlite3.IntegrityError):
        create_relationship(con, Relationship(concept1.id, predicate1.id, 999))

    with pytest.raises(sqlite3.IntegrityError):
        create_relationship(con, Relationship(999, predicate1.id, concept1.id))

    with pytest.raises(sqlite3.IntegrityError):
        create_relationship(con, Relationship(concept1.id, 999, concept2.id))



def test_get_relationship_by_id(con, relationship1):
    res = get_relationship_by_id(con, relationship1.id)

    assert res is not None
    assert res.id == relationship1.id
    assert res.subject_id == relationship1.subject_id
    assert res.predicate_id == relationship1.predicate_id
    assert res.object_id == relationship1.object_id



def test_get_invalid_relationship_by_id(con):
    assert get_relationship_by_id(con, 1) is None



def test_update_relationship(con, relationship1):
    concept3 = create_concept(con, Concept("C++", content = "Something Complicated"))

    assert concept3.id is not None

    relationship2 = Relationship(concept3.id, relationship1.predicate_id, relationship1.object_id, relationship1.id)

    assert update_relationship(con, relationship2)

    assert relationship1.id is not None

    updated_relationship = get_relationship_by_id(con, relationship1.id)

    assert updated_relationship is not None
    assert updated_relationship.id == relationship1.id
    assert updated_relationship.subject_id == relationship2.subject_id
    assert updated_relationship.predicate_id == relationship1.predicate_id
    assert updated_relationship.object_id == relationship1.object_id



def test_update_relationship_with_nonexistent_id(con):
    assert not update_relationship(con, Relationship(1, 1, 2, 999))



def test_update_relationship_with_missing_id(con):
    assert not update_relationship(con, Relationship(1, 1, 2))



def test_delete_relationship(con, relationship1):
    assert delete_relationship(con, relationship1.id)
    assert get_relationship_by_id(con, relationship1.id) is None



def test_delete_nonexistent_relationship(con):
    assert not delete_relationship(con, 1)



def test_delete_referenced_concept(con, relationship1):
    with pytest.raises(sqlite3.IntegrityError):
        delete_concept(con, relationship1.subject_id)

    with pytest.raises(sqlite3.IntegrityError):
        delete_concept(con, relationship1.object_id)



def test_delete_referenced_predicate(con, relationship1):
    with pytest.raises(sqlite3.IntegrityError):
        delete_predicate(con, relationship1.predicate_id)



def test_get_all_relationships(con, relationship1):
    concept3 = create_concept(con, Concept("C++", content = "Something Complicated"))

    assert concept3.id is not None

    table_relationship2 = create_relationship(con, Relationship(concept3.id, relationship1.predicate_id, relationship1.object_id))

    assert table_relationship2.id is not None

    assert get_all_relationships(con) == [get_relationship_by_id(con, relationship1.id), get_relationship_by_id(con, table_relationship2.id)]



def test_get_all_relationships_with_empty_database(con):
    assert get_all_relationships(con) == []



def test_create_project(con, project1):
    res = con.execute("SELECT * FROM projects WHERE id = ?;", (project1.id,)).fetchone()

    assert project1.id is not None
    assert res is not None
    assert res[0] == project1.id
    assert res[1] == project1.title
    assert res[2] == project1.description



def test_get_project_by_id(con, project1):
    res = get_project_by_id(con, project1.id)

    assert res is not None
    assert res.id == project1.id
    assert res.title == project1.title
    assert res.description == project1.description



def test_get_inexistent_project_by_id(con):
    assert get_project_by_id(con, 1) is None



def test_update_project(con, project1):
    project2 = Project("Dissertation", project1.id, "My dissertation")

    assert update_project(con, project2)

    assert project1.id is not None

    updated_project = get_project_by_id(con, project1.id)

    assert updated_project is not None
    assert updated_project.id == project1.id
    assert updated_project.title == project2.title
    assert updated_project.description == project2.description



def test_update_project_with_nonexistent_id(con):
    assert not update_project(con, Project("Thesis", 1, "My thesis"))



def test_update_project_with_missing_id(con):
    assert not update_project(con, Project("Thesis"))



def test_delete_project(con, project1):
    assert delete_project(con, project1.id)
    assert get_project_by_id(con, project1.id) is None



def test_delete_nonexistent_project(con):
    assert not delete_project(con, 1)



def test_delete_project_concepts_for_project(con, project_concept1, project_concept2, project_concept3):
    assert delete_project_concepts_for_project(con, project_concept1.project_id) == 2
    assert delete_project_concepts_for_project(con, project_concept2.project_id) == 1
    assert delete_project_concepts_for_project(con, 999) == 0



def test_get_all_projects(con, project1):
    table_project2 = create_project(con, Project("Portfolio"))

    assert project1.id is not None
    assert table_project2.id is not None

    assert get_all_projects(con) == [
        get_project_by_id(con, project1.id),
        get_project_by_id(con, table_project2.id)
    ]



def test_get_all_projects_with_empty_database(con):
    assert get_all_projects(con) == []



@pytest.mark.parametrize("query, expected_titles", [
    ("Python", ["Python", "Python Testing", "Learning Python"]),
    ("python", ["Python", "Python Testing", "Learning Python"]),
    ("thon", ["Python", "Python Testing", "Learning Python"]),
    ("Java", []),
    ("", ["Python", "Python Testing", "Learning Python"])
])

def test_search_projects_by_title(con, query, expected_titles):
    create_project(con, Project("Python"))
    create_project(con, Project("Python Testing"))
    create_project(con, Project("Learning Python"))

    projects = search_projects_by_title(con, query)

    assert sorted([project.title for project in projects]) == sorted(expected_titles)



def test_create_project_concept(con):
    table_concept = create_concept(con, Concept("Python"))
    table_project = create_project(con, Project("Thesis"))

    assert table_concept.id is not None
    assert table_project.id is not None

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

    assert table_concept.id is not None
    assert table_project.id is not None

    table_project_concept = create_project_concept(con, ProjectConcept(table_concept.id, table_project.id))

    assert table_project_concept.id is not None

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

    assert table_concept1.id is not None
    assert table_project1.id is not None

    table_project_concept = create_project_concept(con, ProjectConcept(table_concept1.id, table_project1.id)
    )

    assert table_concept2.id is not None
    assert table_project2.id is not None

    project_concept2 = ProjectConcept(
        table_concept2.id,
        table_project2.id,
        table_project_concept.id
    )

    assert update_project_concept(con, project_concept2)

    assert table_project_concept.id is not None

    updated_project_concept = get_project_concept_by_id(con, table_project_concept.id)

    assert updated_project_concept is not None
    assert updated_project_concept.id == table_project_concept.id
    assert updated_project_concept.concept_id == project_concept2.concept_id
    assert updated_project_concept.project_id == project_concept2.project_id



def test_update_project_concept_with_nonexistent_id(con):
    table_concept = create_concept(con, Concept("Python"))
    table_project = create_project(con, Project("Thesis"))

    assert table_concept.id is not None
    assert table_project.id is not None

    assert not update_project_concept(con, ProjectConcept(table_concept.id, table_project.id, 999))



def test_update_project_concept_with_missing_id(con):
    assert not update_project_concept(con, ProjectConcept(1, 1))



def test_delete_project_concept(con):
    table_concept = create_concept(con, Concept("Python"))
    table_project = create_project(con, Project("Thesis"))

    assert table_concept.id is not None
    assert table_project.id is not None

    table_project_concept = create_project_concept(con, ProjectConcept(table_concept.id, table_project.id))

    assert table_project_concept.id is not None

    assert delete_project_concept(con, table_project_concept.id)
    assert get_project_concept_by_id(con, table_project_concept.id) is None



def test_delete_nonexistent_project_concept(con):
    assert not delete_project_concept(con, 1)



def test_get_all_project_concepts(con):
    table_concept1 = create_concept(con, Concept("Python"))
    table_concept2 = create_concept(con, Concept("Testing"))
    table_project = create_project(con, Project("Thesis"))

    assert table_concept1.id is not None
    assert table_concept2.id is not None
    assert table_project.id is not None

    table_project_concept1 = create_project_concept(con, ProjectConcept(table_concept1.id, table_project.id))
    table_project_concept2 = create_project_concept(con, ProjectConcept(table_concept2.id, table_project.id))

    assert table_project_concept1.id is not None
    assert table_project_concept2.id is not None

    assert get_all_project_concepts(con) == [
        get_project_concept_by_id(con, table_project_concept1.id),
        get_project_concept_by_id(con, table_project_concept2.id)
    ]



def test_get_all_project_concepts_with_empty_database(con):
    assert get_all_project_concepts(con) == []



def test_create_project_concept_with_nonexistent_concept_id(con):
    table_project = create_project(con, Project("Thesis"))

    assert table_project.id is not None

    with pytest.raises(sqlite3.IntegrityError):
        create_project_concept(con, ProjectConcept(999, table_project.id))



def test_create_project_concept_with_nonexistent_project_id(con):
    table_concept = create_concept(con, Concept("Python"))

    assert table_concept.id is not None

    with pytest.raises(sqlite3.IntegrityError):
        create_project_concept(con, ProjectConcept(table_concept.id, 999))



def test_create_duplicate_project_concept(con):
    table_concept = create_concept(con, Concept("Python"))
    table_project = create_project(con, Project("Thesis"))

    assert table_concept.id is not None
    assert table_project.id is not None

    create_project_concept(con, ProjectConcept(table_concept.id, table_project.id))

    with pytest.raises(sqlite3.IntegrityError):
        create_project_concept(con, ProjectConcept(table_concept.id, table_project.id))



def test_delete_project_with_project_concepts(con):
    table_concept = create_concept(con, Concept("Python"))
    table_project = create_project(con, Project("Thesis"))

    assert table_concept.id is not None
    assert table_project.id is not None

    create_project_concept(con, ProjectConcept(table_concept.id, table_project.id))

    with pytest.raises(sqlite3.IntegrityError):
        delete_project(con, table_project.id)



def test_delete_concept_with_project_concepts(con):
    table_concept = create_concept(con, Concept("Python"))
    table_project = create_project(con, Project("Thesis"))

    assert table_concept.id is not None
    assert table_project.id is not None

    create_project_concept(con, ProjectConcept(table_concept.id, table_project.id))

    with pytest.raises(sqlite3.IntegrityError):
        delete_concept(con, table_concept.id)