from app.schemas import PositiveStrictInt, ConceptCreate, ConceptUpdate, PredicateCreate, PredicateUpdate, RelationshipCreate, RelationshipUpdate, ProjectCreate, ProjectUpdate, ProjectConceptCreate
from pydantic import TypeAdapter, ValidationError
import pytest

adapter = TypeAdapter(PositiveStrictInt)

def test_positive_strict_int():
    assert adapter.validate_python(1) == 1

@pytest.mark.parametrize("val", [0, -1, True, "1",])

def test_positive_strict_int_with_invalid_values(val):
    with pytest.raises(ValidationError):
        adapter.validate_python(val)



@pytest.mark.parametrize("c_title, c_content, expected_content", [
    ("Python", "Something Pythonic", "Something Pythonic"),
    ("Python", None, None),
    ("Python", "", None),
    ("Python", " ", None),
])

def test_create_concept(c_title, c_content, expected_content):
    concept = ConceptCreate(title=c_title, content=c_content)

    assert concept.title == c_title
    assert concept.content == expected_content

@pytest.mark.parametrize("c_title, expected_title", [
    (" Python", "Python"),
    ("Python ", "Python"),
])

def test_create_concept_with_title_blank_spaces(c_title, expected_title):
    concept = ConceptCreate(title=c_title)

    assert concept.title == expected_title

def test_create_concept_with_invalid_title():
    with pytest.raises(ValidationError):
        ConceptCreate(title=1, content="") # type: ignore

def test_create_concept_with_empty_title():
    with pytest.raises(ValidationError):
        ConceptCreate(title=" ", content="")

def test_create_concept_with_invalid_content():
    with pytest.raises(ValidationError):
        ConceptCreate(title="Python", content=1) # type: ignore



@pytest.mark.parametrize("c_title, c_content, expected_content", [
    (None, None, None),
    ("Python", None, None),
    (None, "Something Pythonic", "Something Pythonic"),
    ("Python", "", None),
    ("Python", " ", None)
])

def test_update_concept(c_title, c_content, expected_content):
    concept = ConceptUpdate(title=c_title, content=c_content)

    assert concept.title == c_title
    assert concept.content == expected_content

def test_update_concept_with_missing_fields():
    concept = ConceptUpdate()

    assert concept.title == None
    assert concept.content == None

def test_update_concept_with_invalid_title():
    with pytest.raises(ValidationError):
        ConceptUpdate(title=1) # type: ignore

def test_update_concept_with_empty_title():
    with pytest.raises(ValidationError):
        ConceptUpdate(title=" ")



@pytest.mark.parametrize("p_name, p_bidirectional", [
    ("isA", True),
    ("isA", False),
    (None, True),
])

def test_create_predicate(p_name, p_bidirectional):
    predicate = PredicateCreate(name=p_name, bidirectional=p_bidirectional)

    assert predicate.name == p_name
    assert predicate.bidirectional == p_bidirectional

def test_create_predicate_with_invalid_values():
    with pytest.raises(ValidationError):
        PredicateCreate(name=None, bidirectional=False)

def test_create_predicate_with_missing_values():
    predicate = PredicateCreate()

    assert predicate.name is None
    assert predicate.bidirectional



@pytest.mark.parametrize("p_name, p_bidirectional", [
    ("isA", False),
    ("isA", None),
    (None, None)
])

def test_update_predicate(p_name, p_bidirectional):
    predicate = PredicateUpdate(name=p_name, bidirectional=p_bidirectional)

    assert predicate.name == p_name
    assert predicate.bidirectional == p_bidirectional

def test_update_predicate_with_invalid_values():
    with pytest.raises(ValidationError):
        PredicateUpdate(name=None, bidirectional=False)

def test_update_predicate_with_missing_values():
    predicate = PredicateUpdate()

    assert predicate.name is None
    assert predicate.bidirectional is None



def test_create_relationship():
    relationship = RelationshipCreate(subject_id=1, predicate_id=1, object_id=2)

    assert relationship.subject_id == 1
    assert relationship.predicate_id == 1
    assert relationship.object_id == 2

@pytest.mark.parametrize("s_id, p_id, o_id", [
    (0, 1, 2),
    (1, 0, 2),
    (1, 1, 0)
])

def test_create_relationship_with_zero_ids(s_id, p_id, o_id):
    with pytest.raises(ValidationError):
        RelationshipCreate(subject_id=s_id, predicate_id=p_id, object_id=o_id)

@pytest.mark.parametrize("s_id, p_id, o_id", [
    (-1, 1, 2),
    (1, -1, 2),
    (1, 1, -2)
])

def test_create_relationship_with_negative_ids(s_id, p_id, o_id):
    with pytest.raises(ValidationError):
        RelationshipCreate(subject_id=s_id, predicate_id=p_id, object_id=o_id)

@pytest.mark.parametrize("s_id, p_id, o_id", [
    (True, 1, 2),
    (1, True, 2),
    (1, 1, True)
])

def test_create_relationship_with_boolean_ids(s_id, p_id, o_id):
    with pytest.raises(ValidationError):
        RelationshipCreate(subject_id=s_id, predicate_id=p_id, object_id=o_id)

@pytest.mark.parametrize("s_id, p_id, o_id", [
    ("1", 1, 2),
    (1, "1", 2),
    (1, 1, "2")
])

def test_create_relationship_with_string_ids(s_id, p_id, o_id):
    with pytest.raises(ValidationError):
        RelationshipCreate(subject_id=s_id, predicate_id=p_id, object_id=o_id)



@pytest.mark.parametrize("s_id, p_id, o_id", [
    (1, 1, 2),
    (None, 1, 2),
    (1, None, 2),
    (1, 1, None),
    (None, None, 2),
    (None, 1, None),
    (None, None, 2),
    (None, None, None)
])

def test_update_relationship(s_id, p_id, o_id):
    relationship = RelationshipUpdate(subject_id=s_id, predicate_id=p_id, object_id=o_id)

    assert relationship.subject_id == s_id
    assert relationship.predicate_id == p_id
    assert relationship.object_id == o_id

@pytest.mark.parametrize("s_id, p_id, o_id", [
    (0, 1, 2),
    (1, 0, 2),
    (1, 1, 0),
    (-1, 1, 2),
    (1, -1, 2),
    (1, 1, -2),
    (True, 1, 2),
    (1, True, 2),
    (1, 1, True),
    ("1", 1, 2),
    (1, "1", 2),
    (1, 1, "2")
])

def test_update_relationship_with_invalid_ids(s_id, p_id, o_id):
    with pytest.raises(ValidationError):
        RelationshipUpdate(subject_id=s_id, predicate_id=p_id, object_id=o_id)

def test_update_relationship_with_missing_ids():
    relationship = RelationshipUpdate()

    assert relationship.subject_id is None
    assert relationship.predicate_id is None
    assert relationship.object_id is None



@pytest.mark.parametrize("p_title, p_description, expected_description", [
    ("Thesis", "My thesis", "My thesis"),
    ("Thesis", " My thesis", "My thesis"),
    ("Thesis", "My thesis ", "My thesis"),
    ("Thesis", " ", None),
    ("Thesis", None, None)
])

def test_create_project(p_title, p_description, expected_description):
    project = ProjectCreate(title=p_title, description=p_description)

    assert project.title == p_title
    assert project.description == expected_description

def test_create_project_with_missing_description():
    project = ProjectCreate(title="Thesis")

    assert project.description is None

def test_create_project_with_empty_title():
    with pytest.raises(ValidationError):
        ProjectCreate(title="")

def test_create_project_with_missing_title():
    with pytest.raises(ValidationError):
        ProjectCreate() # type: ignore



@pytest.mark.parametrize("p_title, p_description", [
    ("Thesis", "My thesis"),
    (None, "My thesis"),
    ("Thesis", None),
    (None, None),
])

def test_update_project(p_title, p_description):
    project = ProjectUpdate(title=p_title, description=p_description)

    assert project.title == p_title
    assert project.description == p_description

@pytest.mark.parametrize("p_description, expected_description", [
    (" My thesis", "My thesis"),
    ("My thesis ", "My thesis"),
    (" ", None)
])

def test_update_project_descriptions(p_description, expected_description):
    project = ProjectUpdate(title="Thesis", description=p_description)

    assert project.description == expected_description

def test_update_project_with_missing_args():
    project = ProjectUpdate()

    assert project.title is None
    assert project.description is None

def test_update_project_with_invalid_title():
    with pytest.raises(ValidationError):
        ProjectUpdate(title=" ") # type: ignore



def test_create_project_concept():
    project_concept = ProjectConceptCreate(concept_id=1, project_id=1)

    assert project_concept.concept_id == 1
    assert project_concept.project_id == 1

@pytest.mark.parametrize("c_id, p_id", [
    (0, 1),
    (1, 0),
    (-1, 1),
    (1, -1),
    (True, 1),
    (1, True),
    ("1", 1),
    (1, "1")
])

def test_create_project_concept_with_invalid_fields(c_id, p_id):
    with pytest.raises(ValidationError):
        ProjectConceptCreate(concept_id=c_id, project_id=p_id)

def test_create_project_concept_with_missing_project_id():
    with pytest.raises(ValidationError):
        ProjectConceptCreate(concept_id=1) # type: ignore

def test_create_project_concept_with_missing_concept_id():
    with pytest.raises(ValidationError):
        ProjectConceptCreate(project_id=1) # type: ignore