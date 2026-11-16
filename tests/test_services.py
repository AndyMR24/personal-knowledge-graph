from app.database import get_connection, init_db
from app.exceptions import NotFoundError, DuplicateError
from app.models import Concept, Predicate, Relationship, Project, ProjectConcept
from app.repositories import (
    create_concept,
    get_concept_by_id,
    create_predicate,
    create_relationship,
    get_relationship_by_id,
    create_project,
    create_project_concept,
    get_project_concept_by_id)
from app.services import (
    create_relationship,
    delete_concept,
    add_concept_to_project,
    remove_concept_from_project,
    get_full_graph,
    get_concept_neighborhood)
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
def project_concept1(con, concept1, project1):
    return create_project_concept(con, ProjectConcept(concept1.id, project1.id))



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



def test_add_concept_to_project(con, concept1, project1):
    table_project_concept = add_concept_to_project(con, concept1.id, project1.id)
    
    assert table_project_concept is not None
    assert table_project_concept.id is not None



def test_add_empty_concept_to_project(con, project1):
    with pytest.raises(NotFoundError):
        add_concept_to_project(con, 999, project1.id)



def test_add_concept_to_empty_project(con, concept1):
    with pytest.raises(NotFoundError):
        add_concept_to_project(con, concept1.id, 999)



def test_add_duplicate_project_concept(con, project_concept1):
    with pytest.raises(DuplicateError):
        add_concept_to_project(con, project_concept1.concept_id, project_concept1.project_id)



def test_remove_concept_from_project(con, project_concept1):
    remove_concept_from_project(con, project_concept1)

    assert get_project_concept_by_id(con, project_concept1.id) is None



def test_remove_project_concept_with_missing_id(con):
    with pytest.raises(NotFoundError):
        remove_concept_from_project(con, ProjectConcept(999, 999))



def test_remove_missing_project_concept(con):
    with pytest.raises(NotFoundError):
        remove_concept_from_project(con, ProjectConcept(999, 999, 999))



def test_get_full_graph(con, concept1, concept2, relationship1, relationship1_reversed):
    full_graph = get_full_graph(con)

    assert sorted([concept.title for concept in [concept1, concept2]]) == sorted(concept.title for concept in full_graph[0])

    expected = sorted((r.subject_id, r.predicate_id, r.object_id) for r in [relationship1, relationship1_reversed])

    actual = sorted((r.subject_id, r.predicate_id, r.object_id) for r in full_graph[1])

    assert expected == actual



def test_get_concept_relationship(con):
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

    with pytest.raises(NotFoundError):
        get_concept_neighborhood(con, 999)

    assert get_concept_neighborhood(con, concept1.id) == ([concept1, concept2, concept3], [relationship1, relationship2])
    assert get_concept_neighborhood(con, concept4.id) == ([concept4], [relationship3])
    assert get_concept_neighborhood(con, concept5.id) == ([concept5], [])