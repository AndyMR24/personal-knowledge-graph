from app.database import get_connection, init_db
from app.exceptions import NotFoundError, DuplicateError
from app.models import Concept, Predicate, Relationship, Project, ProjectConcept
from app.repositories import (
    create_concept,
    get_concept_by_id,
    create_predicate,
    get_predicate_by_id,
    create_relationship,
    get_relationship_by_id,
    create_project,
    get_project_by_id,
    get_project_concept_by_id)
from app.services import (
    delete_concept,
    get_concept_neighborhood,
    create_predicate,
    update_predicate,
    delete_predicate,
    create_relationship,
    update_relationship,
    delete_relationship,
    delete_project,
    create_project_concept,
    update_project_concept,
    delete_project_concept,
    get_full_graph)
import app.services
import pytest

@pytest.fixture
def con():
    con = get_connection(":memory:")

    try:
        init_db(con)
        yield con
    finally:
        con.close()

@pytest.fixture
def concept1(con):
    return create_concept(con, Concept("Python", content = "Something Pythonic"))

@pytest.fixture
def concept2(con):
    return create_concept(con, Concept("Programming Language"))

@pytest.fixture
def concept3(con):
    return create_concept(con, Concept("A Third Concept"))

@pytest.fixture
def concept4(con):
    return create_concept(con, Concept("Function"))

@pytest.fixture
def concept_true(con):
    return create_concept(con, Concept("True"))

@pytest.fixture
def predicate1(con):
    return create_predicate(con, Predicate(name = "isA", bidirectional = False))

@pytest.fixture
def predicate2(con):
    return create_predicate(con, Predicate())

@pytest.fixture
def predicate3(con):
    return create_predicate(con, Predicate(name = "from"))

@pytest.fixture
def relationship1(con, concept1, concept2, predicate1):
    return create_relationship(con, Relationship(concept1.id, predicate1.id, concept2.id))

@pytest.fixture
def relationship1_reversed(con, concept1, concept2, predicate1):
    return create_relationship(con, Relationship(concept2.id, predicate1.id, concept1.id))

@pytest.fixture
def relationship2(con, concept1, concept2, predicate2):
    return create_relationship(con, Relationship(concept1.id, predicate2.id, concept2.id))

@pytest.fixture
def relationshipB(con, concept2, concept3, predicate1):
    return create_relationship(con, Relationship(concept2.id, predicate1.id, concept3.id))

@pytest.fixture
def relationship3(con, concept1, concept4, predicate3):
    return create_relationship(con, Relationship(concept4.id, predicate3.id, concept1.id))

@pytest.fixture
def reflexive_relationship(con, concept_true, predicate2):
    return create_relationship(con, Relationship(concept_true.id, predicate2.id, concept_true.id))

@pytest.fixture
def project1(con):
    return create_project(con, Project("Thesis", description = "My Thesis"))

@pytest.fixture
def project2(con):
    return create_project(con, Project("Knowledge Graph"))

@pytest.fixture
def project_concept1(con, concept1, project1):
    return create_project_concept(con, ProjectConcept(concept1.id, project1.id))

@pytest.fixture
def project_concept2(con, concept1, project2):
    return create_project_concept(con, ProjectConcept(concept1.id, project2.id))



def test_delete_concept(con, concept1, relationship1, project_concept1):
    assert delete_concept(con, concept1.id)
    assert get_concept_by_id(con, concept1.id) is None
    assert get_relationship_by_id(con, relationship1.id) is None
    assert get_project_concept_by_id(con, project_concept1.id) is None



def test_delete_inexistent_concept(con):
    with pytest.raises(NotFoundError):
        delete_concept(con, 999)



def test_delete_rollback(con, concept1, relationship1, project_concept1, monkeypatch):
    def failing_delete(con, concept_id):
        raise RuntimeError("Simulated Failure")

    monkeypatch.setattr(app.services, "repositories_delete_concept", failing_delete)

    with pytest.raises(RuntimeError):
        delete_concept(con, concept1.id)

    assert get_concept_by_id(con, concept1.id) is not None
    assert get_relationship_by_id(con, relationship1.id) is not None
    assert get_project_concept_by_id(con, project_concept1.id) is not None



def test_get_concept_neighborhood(con):
    concept1 = create_concept(con, Concept("Python"))
    concept2 = create_concept(con, Concept("Programming Language"))
    concept3 = create_concept(con, Concept("Function"))
    concept4 = create_concept(con, Concept("True"))
    concept5 = create_concept(con, Concept("Java"))

    assert concept1.id is not None
    assert concept2.id is not None
    assert concept3.id is not None
    assert concept4.id is not None
    assert concept5.id is not None

    predicate1 = create_predicate(con, Predicate(name = "isA", bidirectional = False))
    predicate2 = create_predicate(con, Predicate(name = "from", bidirectional = False))
    predicate3 = create_predicate(con, Predicate())

    assert predicate1.id is not None
    assert predicate2.id is not None
    assert predicate3.id is not None

    relationship1 = create_relationship(con, Relationship(concept1.id, predicate1.id, concept2.id))
    relationship2 = create_relationship(con, Relationship(concept3.id, predicate2.id, concept1.id))
    relationship3 = create_relationship(con, Relationship(concept4.id, predicate3.id, concept4.id))

    project1 = create_project(con, Project("A Project Title"))

    assert project1.id is not None

    project_concept1 = create_project_concept(con, ProjectConcept(concept1.id, project1.id))

    with pytest.raises(NotFoundError):
        get_concept_neighborhood(con, 999)

    assert get_concept_neighborhood(con, concept1.id) == {
        "concepts": [concept1, concept2, concept3],
        "predicates": [predicate1, predicate2],
        "relationships": [relationship1, relationship2],
        "projects": [project1],
        "project_concepts": [project_concept1]
    }

    assert get_concept_neighborhood(con, concept4.id) == {
        "concepts": [concept4],
        "predicates": [predicate3],
        "relationships": [relationship3],
        "projects": [],
        "project_concepts": []
    }

    assert get_concept_neighborhood(con, concept5.id) == {
        "concepts": [concept5],
        "predicates": [],
        "relationships": [],
        "projects": [],
        "project_concepts": []
    }



def test_create_predicate(con):
    assert create_predicate(con, Predicate(name = "isA", bidirectional = False)) is not None

    with pytest.raises(DuplicateError):
        create_predicate(con, Predicate(name = "isA", bidirectional = False))

    assert create_predicate(con, Predicate()) is not None

    with pytest.raises(DuplicateError):
        create_predicate(con, Predicate())



def test_update_predicate(con, predicate1, predicate2):    
    update_predicate(con, Predicate(predicate1.id, "isA", True))

    updated_predicate = get_predicate_by_id(con, predicate1.id)

    assert updated_predicate is not None
    assert updated_predicate.name == "isA"
    assert updated_predicate.bidirectional

    with pytest.raises(NotFoundError):
        update_predicate(con, Predicate(999))

    with pytest.raises(DuplicateError):
        update_predicate(con, Predicate(2, "isA"))



def test_delete_predicate(con, predicate1, relationship1, relationship3):
    assert delete_predicate(con, predicate1.id)
    assert get_predicate_by_id(con, predicate1.id) is None
    assert get_relationship_by_id(con, relationship1.id) is None
    assert get_relationship_by_id(con, relationship3.id) is not None



def test_create_relationship(con, relationship1):
    assert get_relationship_by_id(con, relationship1.id) is not None



def test_create_reversed_relationship(con, relationship1, relationship1_reversed):
    assert relationship1.id != relationship1_reversed.id
    assert relationship1.subject_id == relationship1_reversed.object_id
    assert relationship1.predicate_id == relationship1_reversed.predicate_id
    assert relationship1.object_id == relationship1_reversed.subject_id



def test_create_relationship_with_missing_subject(con, predicate1, concept2):
    with pytest.raises(NotFoundError):
        create_relationship(con, Relationship(999, predicate1.id, concept2.id))



def test_create_relationship_with_missing_object(con, concept1, predicate1):
    with pytest.raises(NotFoundError):
        create_relationship(con, Relationship(concept1.id, predicate1.id, 999))



def test_create_relationship_with_missing_predicate(con, concept1, concept2):
    with pytest.raises(NotFoundError):
        create_relationship(con, Relationship(concept1.id, 999, concept2.id))



def test_create_duplicate_relationship(con, relationship1):
    with pytest.raises(DuplicateError):
        create_relationship(con, relationship1)



def test_create_reversed_relationship_with_bidirectional_predicate(con, concept1, concept2, predicate2, relationship2):
    with pytest.raises(DuplicateError):
        create_relationship(con, Relationship(concept2.id, predicate2.id, concept1.id))



def test_create_relationship_cycle(con, concept1, concept3, predicate1, relationship1, relationshipB):
    assert create_relationship(con, Relationship(concept3.id, predicate1.id, concept1.id)) is not None



def test_create_relationship_same_concepts_different_predicates(con, relationship1, concept1, concept2, predicate2):
    assert create_relationship(con, Relationship(concept1.id, predicate2.id, concept2.id)) is not None



@pytest.mark.parametrize("s_id, p_id, o_id", [
    (1, 2, 2),
    (2, 1, 2),
    (1, 1, 1),
    (1, 1, 2)
])

def test_update_relationship(con, s_id, p_id, o_id, concept1, concept2, predicate2, relationship1):
    update_relationship(con, Relationship(s_id, p_id, o_id, relationship1.id))

    updated_relationship = get_relationship_by_id(con, relationship1.id)

    assert updated_relationship is not None
    assert updated_relationship.subject_id == s_id
    assert updated_relationship.predicate_id == p_id
    assert updated_relationship.object_id == o_id



def test_update_inexistent_relationship(con):
    with pytest.raises(NotFoundError):
        update_relationship(con, Relationship(1, 1, 2, 999))



@pytest.mark.parametrize("s_id, p_id, o_id", [
    (999, 1, 2),
    (1, 999, 2),
    (1, 1, 999)
])

def test_update_relationship_with_inexistent_fields(con, s_id, p_id, o_id, relationship1):
    with pytest.raises(NotFoundError):
        update_relationship(con, Relationship(s_id, p_id, o_id, relationship1.id))



def test_update_relationship_to_duplicate(con, relationship1, relationship2):
    with pytest.raises(DuplicateError):
        update_relationship(con, Relationship(relationship1.subject_id, relationship1.predicate_id, relationship1.object_id, relationship2.id))



def test_update_relationship_reversed_duplicate(con, relationship1, relationship2):
    with pytest.raises(DuplicateError):
        update_relationship(con, Relationship(relationship2.object_id, relationship2.predicate_id, relationship2.subject_id, relationship1.id))



def test_delete_relationship(con, concept1, concept2, predicate1, relationship1):
    delete_relationship(con, relationship1.id)

    assert get_relationship_by_id(con, relationship1.id) is None
    assert get_concept_by_id(con, concept1.id) is not None
    assert get_concept_by_id(con, concept2.id) is not None
    assert get_predicate_by_id(con, predicate1.id) is not None



def test_delete_inexistent_relationship(con):
    with pytest.raises(NotFoundError):
        delete_relationship(con, 999)



def test_delete_project(con, concept1, concept2, project1, project2, project_concept1, project_concept2):
    assert delete_project(con, project1.id)
    assert get_project_concept_by_id(con, project_concept1.id) is None
    assert get_project_concept_by_id(con, project_concept2.id) is not None



def test_delete_project_rollback_restores_project_and_memberships(
    con,
    concept1,
    concept2,
    project1,
    project_concept1,
    monkeypatch,
):
    project_concept2 = create_project_concept(
        con,
        ProjectConcept(concept2.id, project1.id),
    )

    def failing_delete_project(con, project_id):
        assert get_project_by_id(con, project_id) == project1
        assert con.execute(
            "SELECT COUNT(*) FROM project_concepts WHERE project_id = ?;",
            (project_id,),
        ).fetchone() == (0,)
        raise RuntimeError("Simulated project deletion failure")

    monkeypatch.setattr(
        app.services,
        "repositories_delete_project",
        failing_delete_project,
    )

    with pytest.raises(RuntimeError, match="Simulated project deletion failure"):
        delete_project(con, project1.id)

    assert get_project_by_id(con, project1.id) == project1
    assert get_project_concept_by_id(con, project_concept1.id) == project_concept1
    assert get_project_concept_by_id(con, project_concept2.id) == project_concept2
    assert con.execute(
        "SELECT COUNT(*) FROM project_concepts WHERE project_id = ?;",
        (project1.id,),
    ).fetchone() == (2,)



def test_add_concept_to_project(con, concept1, project1):
    table_project_concept = create_project_concept(con, ProjectConcept(concept1.id, project1.id))
    
    assert table_project_concept is not None
    assert table_project_concept.id is not None



def test_add_empty_concept_to_project(con, project1):
    with pytest.raises(NotFoundError):
        create_project_concept(con, ProjectConcept(999, project1.id))



def test_add_concept_to_empty_project(con, concept1):
    with pytest.raises(NotFoundError):
        create_project_concept(con, ProjectConcept(concept1.id, 999))



def test_add_duplicate_project_concept(con, project_concept1):
    with pytest.raises(DuplicateError):
        create_project_concept(con, ProjectConcept(project_concept1.concept_id, project_concept1.project_id))



def test_update_project_concept(con, concept2, project_concept1):
    update_project_concept(con, ProjectConcept(concept2.id, project_concept1.project_id, project_concept1.id))

    updated_project_concept = get_project_concept_by_id(con, project_concept1.id)

    assert updated_project_concept is not None
    assert updated_project_concept.id == project_concept1.project_id
    assert updated_project_concept.concept_id == concept2.id
    assert updated_project_concept.project_id == project_concept1.project_id



@pytest.mark.parametrize("c_id, p_id, cp_id", [
    (999, 1, 1),
    (1, 999, 1),
    (1, 1, 999)
])

def test_update_inexistent_project_concept(con, c_id, p_id, cp_id, concept1, project1, project_concept1):
    with pytest.raises(NotFoundError):
        update_project_concept(con, ProjectConcept(c_id, p_id, cp_id))



def test_remove_concept_from_project(con, project_concept1):
    delete_project_concept(con, project_concept1.id)

    assert get_project_concept_by_id(con, project_concept1.id) is None



def test_delete_project_concept_with_inexistent_id(con):
    with pytest.raises(NotFoundError):
        delete_project_concept(con, 999)



def test_get_full_graph(con, concept1, concept2, predicate1, predicate2, relationship1, relationship2, relationship1_reversed, project1, project_concept1):
    full_graph = get_full_graph(con)

    assert full_graph["concepts"] == [concept1, concept2]
    assert full_graph["predicates"] == [predicate1, predicate2]
    assert full_graph["relationships"] == [relationship1, relationship2, relationship1_reversed]
    assert full_graph["projects"] == [project1]
    assert full_graph["project_concepts"] == [project_concept1]
