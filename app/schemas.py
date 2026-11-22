from typing import Annotated
from annotated_types import Gt
from pydantic import BaseModel, StringConstraints, StrictInt, field_validator, model_validator

# Define a string with no whitespaces and at least 1 character
NonEmptyString = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1)
]



PositiveStrictInt = Annotated[
    StrictInt,
    Gt(0)
]



class ConceptCreate(BaseModel):
    title: NonEmptyString
    content: str | None = None

    @field_validator("content", mode="after")
    @classmethod
    def normalize_optional_string(cls, s: str |None) -> str | None:
        if s:
            stripped = s.strip()
            return stripped if stripped else None
        else:
            return None



class ConceptUpdate(BaseModel):
    title: NonEmptyString | None = None
    content: str | None = None

    @field_validator("content", mode="after")
    @classmethod
    def normalize_optional_string(cls, s: str |None) -> str | None:
        if s:
            stripped = s.strip()
            return stripped if stripped else None
        else:
            return None



class PredicateCreate(BaseModel):
    name: NonEmptyString | None = None
    bidirectional: bool = True

    @model_validator(mode="after")
    def validate_default_directionality(self) -> PredicateCreate:
        if self.name is None and not self.bidirectional:
            raise ValueError("A predicate without a name must be bidirectional")

        return self



class PredicateUpdate(BaseModel):
    name: NonEmptyString | None = None
    bidirectional: bool | None = None

    @model_validator(mode="after")
    def validate_updated_predicate(self) -> PredicateUpdate:
        if ("name" in self.model_fields_set and self.name is None and self.bidirectional is False):
            raise ValueError("A predicate without a name must be bidirectional")

        return self



class RelationshipCreate(BaseModel):
    subject_id: StrictInt
    predicate_id: StrictInt
    object_id: StrictInt

    # This is an alternative to using the PositiveStrictInt type, just for having an example of it
    @field_validator("subject_id", "predicate_id", "object_id", mode="after")
    @classmethod
    def validate_id(cls, number: int) -> int:
        if number < 1:
            raise ValueError("The id's must be positive")

        return number



class RelationshipUpdate(BaseModel):
    subject_id: PositiveStrictInt | None = None
    predicate_id: PositiveStrictInt | None = None
    object_id: PositiveStrictInt | None = None



class ProjectCreate(BaseModel):
    title: NonEmptyString
    description: str | None = None

    @field_validator("description", mode="after")
    @classmethod
    def normalize_optional_string(cls, s: str | None) -> str | None:
        if s:
            stripped = s.strip()
            return stripped if stripped else None
        else:
            return None



class ProjectUpdate(BaseModel):
    title: NonEmptyString | None = None
    description: str | None = None

    @field_validator("description", mode="after")
    @classmethod
    def normalize_optional_string(cls, s: str | None) -> str | None:
        if s:
            stripped = s.strip()
            return stripped if stripped else None
        else:
            return None



class ProjectConceptCreate(BaseModel):
    concept_id: PositiveStrictInt
    project_id: PositiveStrictInt