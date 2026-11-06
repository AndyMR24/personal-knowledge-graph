from dataclasses import dataclass

def _validate_required_string(value: str) -> None:
    if not isinstance(value, str):
        raise TypeError("A required string must be a string")

    if not value.strip():
        raise ValueError("A required string must contain non-whitespace text")

def _validate_optional_string(value: str | None) -> None:
    if value is None:
        return

    if not isinstance(value, str):
        raise TypeError("An optional string must be a string or None")

def _validate_required_id(id: int | None) -> None:
    if id is None:
        raise ValueError("This is a required id")

    _validate_id(id)

def _validate_id(id: int | None) -> None:
    if id is None:
        return

    if type(id) is not int:
        raise TypeError("An id has to be an integer or None")

    if id <= 0:
        raise ValueError("An id must be positive")



@dataclass
class Concept:
    title: str
    id: int | None = None
    content: str | None = None

    def __post_init__(self):
        _validate_required_string(self.title)
        _validate_id(self.id)
        _validate_optional_string(self.content)



@dataclass 
class Predicate:
    id: int | None = None
    name: str | None = None
    bidirectional: bool = True

    def __post_init__(self):
        _validate_id(self.id)
        if type(self.bidirectional) is not bool:
            raise TypeError("bidirectional must be a boolean")

        if self.name is None:
            if not self.bidirectional:
                raise ValueError("The generic predicate must be bidirectional")
            return

        _validate_required_string(self.name)



@dataclass
class Relationship:
    subject_id: int
    predicate_id: int
    object_id: int
    id: int | None = None
    remarks: str | None = None

    def __post_init__(self):
        _validate_id(self.id)
        _validate_required_id(self.subject_id)
        _validate_required_id(self.predicate_id)
        _validate_required_id(self.object_id)
        _validate_optional_string(self.remarks)



@dataclass
class Project:
    title: str
    id: int | None = None
    description: str | None = None

    def __post_init__(self):
        _validate_required_string(self.title)
        _validate_id(self.id)
        _validate_optional_string(self.description)



@dataclass
class ProjectConcept:
    concept_id: int
    project_id: int
    id: int | None = None

    def __post_init__(self):
        _validate_id(self.id)
        _validate_required_id(self.concept_id)
        _validate_required_id(self.project_id)
