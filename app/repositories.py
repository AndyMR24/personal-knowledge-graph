from app.models import Concept, Predicate, Relationship, Project, ProjectConcept
import sqlite3

def create_concept(con: sqlite3.Connection, concept: Concept) -> Concept:
    cur = con.cursor()

    try:
        cur.execute("""
            INSERT INTO concepts (title, content) VALUES (?, ?);
        """, (concept.title, concept.content))

        concept_id = cur.lastrowid
    finally:
        cur.close()

    return Concept(concept.title, concept_id, concept.content)



def get_concept_by_id(con: sqlite3.Connection, concept_id: int) -> Concept | None:
    cur = con.cursor()

    try:
        table_concept = cur.execute("""
            SELECT * FROM concepts
            WHERE id = ?;
        """, (concept_id,)).fetchone()
    finally:
        cur.close()

    if table_concept is None:
        return None

    return Concept(table_concept[1], table_concept[0], table_concept[2])



def update_concept(con: sqlite3.Connection, concept: Concept) -> bool:
    if concept.id is None:
        return False

    cur = con.cursor()

    try:
        cur.execute("""
            UPDATE concepts
            SET title = ?, content = ? 
            WHERE id = ?;
        """, (concept.title, concept.content, concept.id))

        changed_rows = cur.rowcount
    finally:
        cur.close()

    return changed_rows == 1



def delete_concept(con: sqlite3.Connection, concept_id: int) -> bool:
    cur = con.cursor()

    try:
        cur.execute("""
            DELETE FROM concepts
            WHERE id = ?;
        """, (concept_id,))

        changed_rows = cur.rowcount
    finally:
        cur.close()

    return changed_rows == 1



def get_all_concepts(con: sqlite3.Connection) -> list[Concept]:
    cur = con.cursor()

    try:
        res = cur.execute("SELECT * FROM concepts;").fetchall()
    finally:
        cur.close()

    if not res:
        return []

    concepts = []

    for i in range(len(res)):
        concepts.append(Concept(res[i][1], res[i][0], res[i][2]))

    return concepts



def search_concepts_by_title(con: sqlite3.Connection, title: str) -> list[Concept]:
    cur = con.cursor()

    try:
        concepts = cur.execute("""
            SELECT * FROM concepts
            WHERE title LIKE ?;
        """, (f'%{title}%',)).fetchall()
    finally:
        cur.close()

    res = []

    for row in concepts:
        res.append(Concept(row[1], row[0], row[2]))

    return res



def delete_relationships_for_concept(con: sqlite3.Connection, concept_id: int) -> int: 
    cur = con.cursor()

    try:
        cur.execute("""
            DELETE FROM relationships
            WHERE subject_id = ? OR object_id = ?;
        """, (concept_id, concept_id))

        changed_rows = cur.rowcount
    finally:
        cur.close()

    return changed_rows



def delete_project_concepts_for_concept(con: sqlite3.Connection, concept_id: int) -> int:
    cur = con.cursor()

    try:
        cur.execute("""
            DELETE FROM project_concepts
            WHERE concept_id = ?;
        """, (concept_id,))

        changed_rows = cur.rowcount
    finally:
        cur.close()

    return changed_rows



def create_predicate(con: sqlite3.Connection, predicate: Predicate) -> Predicate:
    cur = con.cursor()

    try:
        cur.execute("""
            INSERT INTO predicates (name, bidirectional) VALUES (?, ?);
        """, (predicate.name, predicate.bidirectional))

        predicate_id = cur.lastrowid
    finally:
        cur.close()

    return Predicate(predicate_id, predicate.name, predicate.bidirectional)



def get_predicate_by_id(con: sqlite3.Connection, predicate_id: int) -> Predicate | None:
    cur = con.cursor()

    try:
        table_predicate = cur.execute("""
            SELECT * FROM predicates
            WHERE id = ?;
            """, (predicate_id,)).fetchone()
    finally:
        cur.close()

    if table_predicate is None:
        return None

    return Predicate(table_predicate[0], table_predicate[1], bool(table_predicate[2]))



def get_predicate_by_name(con:sqlite3.Connection, predicate_name: str | None = None) -> Predicate | None:
    cur = con.cursor()

    try:
        if predicate_name is None:
            table_predicate = cur.execute("""
                SELECT * FROM predicates
                WHERE name IS NULL;
            """).fetchone()
        else:    
            table_predicate = cur.execute("""
                SELECT * FROM predicates
                WHERE name = ?;
            """, (predicate_name,)).fetchone()
    finally:
        cur.close()

    if table_predicate is None:
        return None

    return Predicate(table_predicate[0], table_predicate[1], bool(table_predicate[2]))



def update_predicate(con: sqlite3.Connection, predicate: Predicate) -> bool:
    if predicate.id is None:
        return False

    cur = con.cursor()

    try:
        cur.execute("""
            UPDATE predicates
            SET name = ?, bidirectional = ? 
            WHERE id = ?;
        """, (predicate.name, predicate.bidirectional, predicate.id))

        changed_rows = cur.rowcount
    finally:
        cur.close()

    return changed_rows == 1



def delete_predicate(con: sqlite3.Connection, predicate_id: int) -> bool:
    cur = con.cursor()

    try:
        cur.execute("""
            DELETE FROM predicates
            WHERE id = ?;
        """, (predicate_id,))

        changed_rows = cur.rowcount
    finally:
        cur.close()

    return changed_rows == 1



def get_all_predicates(con: sqlite3.Connection) -> list[Predicate]:
    cur = con.cursor()

    try:
        res = cur.execute("SELECT * FROM predicates;").fetchall()
    finally:
        cur.close()

    if not res:
        return []

    predicates = []

    for i in range(len(res)):
        predicates.append(Predicate(res[i][0], res[i][1], bool(res[i][2])))

    return predicates



def delete_relationships_for_predicate(con: sqlite3.Connection, predicate_id: int) -> int:
    cur = con.cursor()

    try:
        cur.execute("""
            DELETE FROM relationships
            WHERE predicate_id = ?;
        """, (predicate_id,))

        changed_rows = cur.rowcount
    finally:
        cur.close()

    return changed_rows



def create_relationship(con: sqlite3.Connection, relationship: Relationship) -> Relationship:
    cur = con.cursor()

    try:
        cur.execute("""
            INSERT INTO relationships (subject_id, predicate_id, object_id) VALUES (?, ?, ?);
        """, (relationship.subject_id, relationship.predicate_id, relationship.object_id))

        relationship_id = cur.lastrowid
    finally:
        cur.close()

    return Relationship(relationship.subject_id, relationship.predicate_id, relationship.object_id, relationship_id)



def get_relationship_by_id(con: sqlite3.Connection, relationship_id: int) -> Relationship | None:
    cur = con.cursor()

    try:
        table_relationship = cur.execute("SELECT * FROM relationships WHERE id = ?;", (relationship_id,)).fetchone()
    finally:
        cur.close()

    if table_relationship is None:
        return None

    return Relationship(table_relationship[1], table_relationship[2], table_relationship[3], table_relationship[0])



def update_relationship(con: sqlite3.Connection, relationship: Relationship) -> bool:
    if relationship.id is None:
        return False

    cur = con.cursor()

    try:
        cur.execute("""
            UPDATE relationships
            SET subject_id = ?, predicate_id = ?, object_id = ? 
            WHERE id = ?;
        """, (relationship.subject_id, relationship.predicate_id, relationship.object_id, relationship.id))

        changed_rows = cur.rowcount
    finally:
        cur.close()

    return changed_rows == 1



def delete_relationship(con: sqlite3.Connection, relationship_id: int) -> bool:
    cur = con.cursor()

    try:
        cur.execute("""
            DELETE FROM relationships
            WHERE id = ?;
        """, (relationship_id,))

        changed_rows = cur.rowcount
    finally:
        cur.close()

    return changed_rows == 1



def get_all_relationships(con: sqlite3.Connection) -> list[Relationship]:
    cur = con.cursor()

    try:
        res = cur.execute("SELECT * FROM relationships;").fetchall()
    finally:
        cur.close()

    if not res:
        return []

    relationships = []

    for i in range(len(res)):
        relationships.append(Relationship(res[i][1], res[i][2], res[i][3], res[i][0]))

    return relationships



def create_project(con: sqlite3.Connection, project: Project) -> Project:
    cur = con.cursor()

    try:
        cur.execute("""
            INSERT INTO projects (title, description) VALUES (?, ?);
        """, (project.title, project.description))

        project_id = cur.lastrowid
    finally:
        cur.close()

    return Project(project.title, project_id, project.description)



def get_project_by_id(con: sqlite3.Connection, project_id: int) -> Project | None:
    cur = con.cursor()

    try:
        table_project = cur.execute("""
            SELECT * FROM projects
            WHERE id = ?;
        """, (project_id,)).fetchone()
    finally:
        cur.close()

    if table_project is None:
        return None

    return Project(table_project[1], table_project[0], table_project[2])



def update_project(con: sqlite3.Connection, project: Project) -> bool:
    if project.id is None:
        return False

    cur = con.cursor()

    try:
        cur.execute("""
            UPDATE projects
            SET title = ?, description = ?
            WHERE id = ?;
        """, (project.title, project.description, project.id))

        changed_rows = cur.rowcount
    finally:
        cur.close()

    return changed_rows == 1



def delete_project(con: sqlite3.Connection, project_id: int) -> bool:
    cur = con.cursor()

    try:
        cur.execute("""
            DELETE FROM projects
            WHERE id = ?;
        """, (project_id,))

        changed_rows = cur.rowcount
    finally:
        cur.close()

    return changed_rows == 1



def delete_project_concepts_for_project(con: sqlite3.Connection, project_id: int) -> int:
    cur = con.cursor()

    try:
        cur.execute("""
            DELETE FROM project_concepts
            WHERE project_id = ?;
        """, (project_id,))

        changed_rows = cur.rowcount
    finally:
        cur.close()

    return changed_rows



def get_all_projects(con: sqlite3.Connection) -> list[Project]:
    cur = con.cursor()

    try:
        res = cur.execute("SELECT * FROM projects;").fetchall()
    finally:
        cur.close()

    if not res:
        return []

    projects = []

    for i in range(len(res)):
        projects.append(Project(res[i][1], res[i][0], res[i][2]))

    return projects



def search_projects_by_title(con: sqlite3.Connection, title: str) -> list[Project]:
    cur = con.cursor()

    try:
        projects = cur.execute("""
            SELECT * FROM projects
            WHERE title LIKE ?;
        """, (f'%{title}%',)).fetchall()
    finally:
        cur.close()

    res = []

    for row in projects:
        res.append(Project(row[1], row[0], row[2]))

    return res



def create_project_concept(con: sqlite3.Connection, project_concept: ProjectConcept) -> ProjectConcept:
    cur = con.cursor()

    try:
        cur.execute("""
            INSERT INTO project_concepts (concept_id, project_id) VALUES (?, ?);
        """, (project_concept.concept_id, project_concept.project_id))

        project_concept_id = cur.lastrowid
    finally:
        cur.close()

    return ProjectConcept(
        project_concept.concept_id,
        project_concept.project_id,
        project_concept_id
    )



def get_project_concept_by_id(con: sqlite3.Connection, project_concept_id: int) -> ProjectConcept | None:
    cur = con.cursor()

    try:
        table_project_concept = cur.execute(
            "SELECT * FROM project_concepts WHERE id = ?;",
            (project_concept_id,)
        ).fetchone()
    finally:
        cur.close()

    if table_project_concept is None:
        return None

    return ProjectConcept(
        table_project_concept[1],
        table_project_concept[2],
        table_project_concept[0]
    )



def update_project_concept(con: sqlite3.Connection, project_concept: ProjectConcept) -> bool:
    if project_concept.id is None:
        return False

    cur = con.cursor()

    try:
        cur.execute("""
            UPDATE project_concepts
            SET concept_id = ?, project_id = ?
            WHERE id = ?;
        """, (
            project_concept.concept_id,
            project_concept.project_id,
            project_concept.id
        ))

        changed_rows = cur.rowcount
    finally:
        cur.close()

    return changed_rows == 1



def delete_project_concept(con: sqlite3.Connection, project_concept_id: int) -> bool:
    cur = con.cursor()

    try:
        cur.execute("""
            DELETE FROM project_concepts
            WHERE id = ?;
        """, (project_concept_id,))

        changed_rows = cur.rowcount
    finally:
        cur.close()

    return changed_rows == 1



def get_all_project_concepts(con: sqlite3.Connection) -> list[ProjectConcept]:
    cur = con.cursor()

    try:
        res = cur.execute("SELECT * FROM project_concepts;").fetchall()
    finally:
        cur.close()

    if not res:
        return []

    project_concepts = []

    for i in range(len(res)):
        project_concepts.append(
            ProjectConcept(res[i][1], res[i][2], res[i][0])
        )

    return project_concepts