# Personal Knowledge Graph User Manual

This manual describes how to use the interface. For installation, architecture, API details, and test commands, see [README.md](README.md).

## Personalize the Header

Click the application name in the upper-left corner. Enter your name in the form and save it.

For example, entering `Alice` changes the header to `Alice's`. The browser remembers the name locally. Clear the field to restore `User`.

## Explore the Graph

Concepts appear as colored circles. Projects appear as colored rounded rectangles when project visibility is enabled.

- Larger concepts have more visible connections.
- Directed relationships show one arrowhead.
- Bidirectional relationships show arrowheads at both ends.
- Dotted project links have no text label.
- Self-relationships use a rounded loop around their concept.

Use the search bar to find concepts and projects. Drag the canvas to pan, scroll to zoom, and use **Recenter** to fit the visible graph.

Click a concept or project to open its details on the right. Click a relationship line to inspect that relationship. Close the panel or press Escape to return to the graph.

Use the **Projects** switch to show or hide project nodes and their project links.

## Create and Edit Content

Open **Create** and choose:

- **Concept** for notes and technical ideas
- **Project** for a group of related concepts
- **Relationship** for a concept-to-concept connection
- **Project Link** for adding a concept to a project
- **Predicates** for managing reusable relationship types

The details panel provides **Edit** and **Delete** actions for concepts, projects, and relationships.

### Relationships and predicates

The relationship form lists the predicates that currently exist.

Choose **Create new predicate...** to enter a predicate name and directionality without leaving the relationship form. Existing predicates remain available from the same list.

### Project links

A project can be connected to an existing concept from:

- **Create → Project Link**
- The **Add** action in a project's Concepts section
- The **Add** action in a concept's Projects section

Project memberships can be removed from either the project details or concept details.

## Notes and Markdown

Concept notes and project descriptions support:

- Headings
- Paragraphs
- Bulleted and numbered lists
- Bold and italic text
- Inline code and fenced code blocks
- Blockquotes
- Horizontal rules
- HTTP, HTTPS, and mailto links

Stored HTML is displayed as text rather than interpreted. Unsafe link protocols are not turned into clickable links.

## Validation and Feedback

Forms show required-field and API validation errors without closing. Duplicate predicates, relationships, and memberships are reported in the form or a notification.

Successful changes refresh the graph and relevant details while preserving the current search, project visibility, and selected item when it still exists.

Deleting a project with memberships asks for confirmation and removes those links first. If cleanup fails, the project is not deleted.

If the graph reports that it cannot load, confirm that the application server is still running. Setup commands are in [README.md](README.md).
