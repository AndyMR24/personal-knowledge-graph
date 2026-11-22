import pytest

from app.models import (
    Concept,
    Predicate,
    Project,
    ProjectConcept,
    Relationship,
    _validate_id,
    _validate_required_id,
)


OPTIONAL_ID_MODELS = [
    pytest.param(Concept, {"title": "Python"}, id="concept"),
    pytest.param(Predicate, {"name": "depends_on"}, id="predicate"),
    pytest.param(
        Relationship,
        {"subject_id": 1, "predicate_id": 2, "object_id": 3},
        id="relationship",
    ),
    pytest.param(Project, {"title": "Milestone 2"}, id="project"),
    pytest.param(
        ProjectConcept,
        {"concept_id": 1, "project_id": 2},
        id="project-concept",
    ),
]

REQUIRED_ID_FIELDS = [
    pytest.param(
        Relationship,
        "subject_id",
        {"predicate_id": 2, "object_id": 3},
        id="relationship-subject-id",
    ),
    pytest.param(
        Relationship,
        "predicate_id",
        {"subject_id": 1, "object_id": 3},
        id="relationship-predicate-id",
    ),
    pytest.param(
        Relationship,
        "object_id",
        {"subject_id": 1, "predicate_id": 2},
        id="relationship-object-id",
    ),
    pytest.param(
        ProjectConcept,
        "concept_id",
        {"project_id": 2},
        id="project-concept-concept-id",
    ),
    pytest.param(
        ProjectConcept,
        "project_id",
        {"concept_id": 1},
        id="project-concept-project-id",
    ),
]

REQUIRED_STRING_FIELDS = [
    pytest.param(Concept, "title", {}, id="concept-title"),
    pytest.param(Project, "title", {}, id="project-title"),
]

OPTIONAL_STRING_FIELDS = [
    pytest.param(
        Concept,
        "content",
        {"title": "Python"},
        id="concept-content",
    ),
    pytest.param(
        Project,
        "description",
        {"title": "Thesis"},
        id="project-description",
    ),
]


@pytest.mark.parametrize("id_value", [None, 1, 42])
def test_validate_id_accepts_optional_ids(id_value):
    assert _validate_id(id_value) is None


@pytest.mark.parametrize(
    ("id_value", "expected_exception"),
    [
        pytest.param(0, ValueError, id="zero"),
        pytest.param(-1, ValueError, id="negative"),
        pytest.param("1", TypeError, id="string"),
        pytest.param(True, TypeError, id="true"),
        pytest.param(False, TypeError, id="false"),
        pytest.param(1.5, TypeError, id="float"),
    ],
)
def test_validate_id_rejects_invalid_ids(id_value, expected_exception):
    with pytest.raises(expected_exception):
        _validate_id(id_value)


@pytest.mark.parametrize("model_class, model_kwargs", OPTIONAL_ID_MODELS)
@pytest.mark.parametrize("id_value", [None, 1, 42])
def test_models_accept_optional_ids(model_class, model_kwargs, id_value):
    model = model_class(id=id_value, **model_kwargs)

    assert model.id == id_value


@pytest.mark.parametrize("model_class, model_kwargs", OPTIONAL_ID_MODELS)
@pytest.mark.parametrize("id_value", [True, False])
def test_models_reject_boolean_optional_ids(model_class, model_kwargs, id_value):
    with pytest.raises(TypeError):
        model_class(id=id_value, **model_kwargs)


@pytest.mark.parametrize("id_value", [1, 42])
def test_validate_required_id_accepts_positive_ids(id_value):
    assert _validate_required_id(id_value) is None


@pytest.mark.parametrize(
    ("id_value", "expected_exception"),
    [
        pytest.param(None, ValueError, id="none"),
        pytest.param(0, ValueError, id="zero"),
        pytest.param(-1, ValueError, id="negative"),
        pytest.param("1", TypeError, id="string"),
        pytest.param(True, TypeError, id="true"),
        pytest.param(False, TypeError, id="false"),
        pytest.param(1.5, TypeError, id="float"),
    ],
)
def test_validate_required_id_rejects_invalid_ids(id_value, expected_exception):
    with pytest.raises(expected_exception):
        _validate_required_id(id_value)


@pytest.mark.parametrize("model_class, field_name, other_ids", REQUIRED_ID_FIELDS)
@pytest.mark.parametrize("id_value", [1, 42])
def test_models_accept_positive_required_ids(
    model_class, field_name, other_ids, id_value
):
    model = model_class(**other_ids, **{field_name: id_value})

    assert getattr(model, field_name) == id_value


@pytest.mark.parametrize("model_class, field_name, other_ids", REQUIRED_ID_FIELDS)
def test_models_reject_none_required_ids(model_class, field_name, other_ids):
    with pytest.raises(ValueError):
        model_class(**other_ids, **{field_name: None})


@pytest.mark.parametrize("model_class, field_name, other_ids", REQUIRED_ID_FIELDS)
@pytest.mark.parametrize("id_value", [True, False])
def test_models_reject_boolean_required_ids(
    model_class, field_name, other_ids, id_value
):
    with pytest.raises(TypeError):
        model_class(**other_ids, **{field_name: id_value})


@pytest.mark.parametrize("model_class, field_name, other_values", REQUIRED_STRING_FIELDS)
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param("Python", "Python", id="simple"),
        pytest.param("  Python  ", "Python", id="surrounding-whitespace"),
        pytest.param("Two words", "Two words", id="internal-whitespace"),
    ],
)
def test_normalize_required_strings(
    model_class, field_name, other_values, value, expected
):
    model = model_class(**other_values, **{field_name: value})

    assert getattr(model, field_name) == expected


@pytest.mark.parametrize("model_class, field_name, other_values", REQUIRED_STRING_FIELDS)
@pytest.mark.parametrize(
    "value",
    [
        pytest.param("", id="empty"),
        pytest.param("   ", id="spaces"),
        pytest.param("\t\r\n", id="whitespace"),
    ],
)
def test_models_reject_empty_required_strings(
    model_class, field_name, other_values, value
):
    with pytest.raises(ValueError):
        model_class(**other_values, **{field_name: value})


@pytest.mark.parametrize("model_class, field_name, other_values", REQUIRED_STRING_FIELDS)
@pytest.mark.parametrize(
    "value",
    [
        pytest.param(None, id="none"),
        pytest.param(1, id="integer"),
        pytest.param(True, id="boolean"),
        pytest.param([], id="list"),
        pytest.param(object(), id="object"),
    ],
)
def test_models_reject_non_string_required_values(
    model_class, field_name, other_values, value
):
    with pytest.raises(TypeError):
        model_class(**other_values, **{field_name: value})


@pytest.mark.parametrize("model_class, field_name, other_values", OPTIONAL_STRING_FIELDS)
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param(None, None, id="none"),
        pytest.param("", None, id="empty"),
        pytest.param("   ", None, id="whitespace-only"),
        pytest.param("  Details  ", "Details", id="surrounding-whitespace"),
        pytest.param(
            "First line\nSecond line",
            "First line\nSecond line",
            id="multiline",
        ),
    ],
)
def test_normalize_optional_strings(
    model_class, field_name, other_values, value, expected
):
    model = model_class(**other_values, **{field_name: value})

    assert getattr(model, field_name) == expected


@pytest.mark.parametrize(
    "factory",
    [
        pytest.param(lambda: Concept(), id="concept-title"),
        pytest.param(
            lambda: Relationship(predicate_id=2, object_id=3),
            id="relationship-subject-id",
        ),
        pytest.param(
            lambda: Relationship(subject_id=1, object_id=3),
            id="relationship-predicate-id",
        ),
        pytest.param(
            lambda: Relationship(subject_id=1, predicate_id=2),
            id="relationship-object-id",
        ),
        pytest.param(lambda: Project(), id="project-title"),
        pytest.param(
            lambda: ProjectConcept(project_id=2),
            id="project-concept-concept-id",
        ),
        pytest.param(
            lambda: ProjectConcept(concept_id=1),
            id="project-concept-project-id",
        ),
    ],
)
def test_required_constructor_arguments_are_required(factory):
    with pytest.raises(TypeError):
        factory()


@pytest.mark.parametrize(
    "model, expected",
    [
        pytest.param(
            Concept("Python"),
            {"title": "Python", "id": None, "content": None},
            id="concept",
        ),
        pytest.param(
            Predicate(),
            {"id": None, "name": None, "bidirectional": True},
            id="predicate",
        ),
        pytest.param(
            Relationship(1, 2, 3),
            {
                "subject_id": 1,
                "predicate_id": 2,
                "object_id": 3,
                "id": None,
            },
            id="relationship",
        ),
        pytest.param(
            Project("Thesis"),
            {"title": "Thesis", "id": None, "description": None},
            id="project",
        ),
        pytest.param(
            ProjectConcept(1, 2),
            {"concept_id": 1, "project_id": 2, "id": None},
            id="project-concept",
        ),
    ],
)
def test_models_apply_optional_defaults(model, expected):
    for field_name, value in expected.items():
        assert getattr(model, field_name) == value


@pytest.mark.parametrize(
    "model, expected",
    [
        pytest.param(
            Concept("Python", 7, "Markdown"),
            {"title": "Python", "id": 7, "content": "Markdown"},
            id="concept",
        ),
        pytest.param(
            Predicate(7, "related_to", False),
            {"id": 7, "name": "related_to", "bidirectional": False},
            id="predicate",
        ),
        pytest.param(
            Relationship(1, 2, 3, 7),
            {
                "subject_id": 1,
                "predicate_id": 2,
                "object_id": 3,
                "id": 7,
            },
            id="relationship",
        ),
        pytest.param(
            Project("Thesis", 7, "Description"),
            {"title": "Thesis", "id": 7, "description": "Description"},
            id="project",
        ),
        pytest.param(
            ProjectConcept(1, 2, 7),
            {"concept_id": 1, "project_id": 2, "id": 7},
            id="project-concept",
        ),
    ],
)
def test_models_store_all_constructor_values(model, expected):
    for field_name, value in expected.items():
        assert getattr(model, field_name) == value


@pytest.mark.parametrize("bidirectional", [True, False])
def test_named_predicate_accepts_boolean_directionality(bidirectional):
    predicate = Predicate(name="related_to", bidirectional=bidirectional)

    assert predicate.bidirectional is bidirectional


def test_generic_predicate_must_be_bidirectional():
    with pytest.raises(ValueError):
        Predicate(name=None, bidirectional=False)


@pytest.mark.parametrize(
    "name",
    [
        pytest.param("related_to", id="simple"),
        pytest.param("related to", id="surrounding-whitespace"),
    ],
)
def test_named_predicate_preserves_valid_names(name):
    predicate = Predicate(name=name)

    assert predicate.name == name


@pytest.mark.parametrize(
    "name",
    [
        pytest.param("", id="empty"),
        pytest.param("   ", id="spaces"),
        pytest.param("\t\r\n", id="whitespace"),
    ],
)
def test_named_predicate_rejects_empty_names(name):
    with pytest.raises(ValueError):
        Predicate(name=name)


@pytest.mark.parametrize(
    "name",
    [
        pytest.param(1, id="integer"),
        pytest.param(True, id="boolean"),
        pytest.param([], id="list"),
        pytest.param(object(), id="object"),
    ],
)
def test_predicate_rejects_non_string_names(name):
    with pytest.raises(TypeError):
        Predicate(name=name)


@pytest.mark.parametrize(
    "bidirectional",
    [
        pytest.param(0, id="zero"),
        pytest.param(1, id="one"),
        pytest.param("True", id="string"),
        pytest.param(None, id="none"),
        pytest.param(1.0, id="float"),
    ],
)
def test_predicate_rejects_non_boolean_directionality(bidirectional):
    with pytest.raises(TypeError):
        Predicate(name="related_to", bidirectional=bidirectional)
