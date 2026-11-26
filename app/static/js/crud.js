import { api } from "./api.js";
import {
    confirmDialog,
    openFormModal,
    openModal,
    showToast,
} from "./ui.js";

function optionalText(value) {
    const trimmed = String(value ?? "").trim();
    return trimmed || null;
}

function displayError(error) {
    return error?.message || "The operation could not be completed.";
}

async function assertCurrentGraphReferences(checks) {
    const graph = await api.graph.get();
    for (const check of checks) {
        const collection = graph[check.collection];
        if (!collection.some(item => item.id === check.id)) {
            throw new Error(
                `${check.label} no longer exists. Close this form and try again after the graph refreshes.`,
            );
        }
    }
    return graph;
}

function button(label, className = "secondary-button") {
    const element = document.createElement("button");
    element.type = "button";
    element.className = className;
    element.textContent = label;
    return element;
}

async function saveConcept(concept, onSaved) {
    const payload = {
        title: String(concept.title ?? "").trim(),
        content: optionalText(concept.content),
    };
    const isEdit = Boolean(concept.id);
    const saved = isEdit
        ? await api.concepts.update(concept.id, payload)
        : await api.concepts.create(payload);

    await onSaved(saved, { type: "concept", action: isEdit ? "updated" : "created" });
    showToast(`Concept ${isEdit ? "updated" : "created"}.`);
}

export function openConceptForm({ concept = null, onSaved }) {
    return openFormModal({
        title: concept ? "Edit concept" : "Create concept",
        description: concept
            ? "Update the title or Markdown notes for this concept."
            : "Add a new concept and optional Markdown notes to the graph.",
        submitLabel: concept ? "Save concept" : "Create concept",
        fields: [
            {
                name: "title",
                label: "Title",
                required: true,
                placeholder: "For example, Python decorators",
            },
            {
                name: "content",
                label: "Markdown notes",
                type: "textarea",
                rows: 9,
                placeholder: "# Key ideas\n\nAdd notes, links, and examples...",
            },
        ],
        initialValues: {
            title: concept?.title ?? "",
            content: concept?.content ?? "",
        },
        onSubmit: values => saveConcept({ ...concept, ...values }, onSaved),
    });
}

export async function deleteConcept({
    concept,
    relationshipCount = 0,
    membershipCount = 0,
    onDeleted,
    onRefresh,
}) {
    const details = [];
    if (relationshipCount) {
        details.push(`${relationshipCount} relationship${relationshipCount === 1 ? "" : "s"}`);
    }
    if (membershipCount) {
        details.push(`${membershipCount} project membership${membershipCount === 1 ? "" : "s"}`);
    }
    const consequence = details.length
        ? ` This will remove ${details.join(" and ")}.`
        : "";

    const confirmed = await confirmDialog({
        title: "Delete concept?",
        message: `Delete “${concept.title}”?${consequence}`,
        confirmLabel: "Delete concept",
        destructive: true,
    });
    if (!confirmed) {
        return;
    }

    try {
        await api.concepts.remove(concept.id);
        await onDeleted?.(concept);
        showToast("Concept deleted.");
    } catch (error) {
        await onRefresh?.();
        showToast(`Concept was not deleted. ${displayError(error)}`, "error");
    }
}

async function saveProject(project, onSaved) {
    const payload = {
        title: String(project.title ?? "").trim(),
        description: optionalText(project.description),
    };
    const isEdit = Boolean(project.id);
    const saved = isEdit
        ? await api.projects.update(project.id, payload)
        : await api.projects.create(payload);

    await onSaved(saved, { type: "project", action: isEdit ? "updated" : "created" });
    showToast(`Project ${isEdit ? "updated" : "created"}.`);
}

export function openProjectForm({ project = null, onSaved }) {
    return openFormModal({
        title: project ? "Edit project" : "Create project",
        description: project
            ? "Update this project’s title and description."
            : "Create a project to organize related concepts.",
        submitLabel: project ? "Save project" : "Create project",
        fields: [
            {
                name: "title",
                label: "Title",
                required: true,
                placeholder: "For example, Backend engineering",
            },
            {
                name: "description",
                label: "Description",
                type: "textarea",
                rows: 6,
                placeholder: "What is this project about?",
            },
        ],
        initialValues: {
            title: project?.title ?? "",
            description: project?.description ?? "",
        },
        onSubmit: values => saveProject({ ...project, ...values }, onSaved),
    });
}

export async function deleteProject({
    project,
    memberships = [],
    onDeleted,
    onRefresh,
}) {
    const membershipCopy = memberships.length
        ? ` Its ${memberships.length} project membership${memberships.length === 1 ? "" : "s"} will be removed first.`
        : "";
    const confirmed = await confirmDialog({
        title: "Delete project?",
        message: `Delete “${project.title}”?${membershipCopy} Concepts and their relationships will remain.`,
        confirmLabel: "Delete project",
        destructive: true,
    });
    if (!confirmed) {
        return;
    }

    let removedMemberships = 0;
    try {
        for (const membership of memberships) {
            await api.memberships.remove(membership.id);
            removedMemberships += 1;
        }

        await api.projects.remove(project.id);
        await onDeleted?.(project);
        showToast("Project deleted.");
    } catch (error) {
        await onRefresh?.();
        const partial = removedMemberships > 0
            ? ` Removed ${removedMemberships} of ${memberships.length} memberships first.`
            : "";
        showToast(
            `Project was not deleted.${partial} ${displayError(error)}`,
            "error",
        );
    }
}

export function openPredicateForm({ predicate = null, onSaved, onCancel = null }) {
    return openFormModal({
        title: predicate ? "Edit predicate" : "Create predicate",
        description: "A predicate describes the relationship between two concepts.",
        submitLabel: predicate ? "Save predicate" : "Create predicate",
        fields: [
            {
                name: "name",
                label: "Name",
                placeholder: "For example, depends_on",
                instructions: "Leave blank for an unnamed predicate.",
            },
            {
                name: "bidirectional",
                label: "Bidirectional",
                type: "checkbox",
            },
        ],
        initialValues: {
            name: predicate?.name ?? "",
            bidirectional: predicate?.bidirectional ?? true,
        },
        validate: values => (
            !String(values.name ?? "").trim() && !values.bidirectional
                ? "An unnamed predicate must be bidirectional."
                : null
        ),
        onSubmit: async values => {
            const payload = {
                name: optionalText(values.name),
                bidirectional: Boolean(values.bidirectional),
            };
            const saved = predicate
                ? await api.predicates.update(predicate.id, payload)
                : await api.predicates.create(payload);
            await onSaved(saved);
            showToast(`Predicate ${predicate ? "updated" : "created"}.`);
        },
        onCancel,
    });
}

function predicateRow(predicate, relationships, onEdit, onDelete) {
    const row = document.createElement("div");
    row.className = "manager-row";

    const copy = document.createElement("div");
    copy.className = "manager-row-copy";
    const title = document.createElement("strong");
    title.textContent = predicate.name || "related to";
    const meta = document.createElement("span");
    const relationshipCount = relationships.filter(
        relationship => relationship.predicate_id === predicate.id,
    ).length;
    meta.textContent = `${predicate.bidirectional ? "Bidirectional" : "Directed"} · ${relationshipCount} relationship${relationshipCount === 1 ? "" : "s"}`;
    copy.append(title, meta);

    const actions = document.createElement("div");
    actions.className = "manager-row-actions";
    const edit = button("Edit", "small-button");
    const remove = button("Delete", "small-button small-button-danger");
    edit.addEventListener("click", () => onEdit(predicate));
    remove.addEventListener("click", () => onDelete(predicate));
    actions.append(edit, remove);

    row.append(copy, actions);
    return row;
}

export function openPredicateManager({ data, onChanged }) {
    let predicates = [...data.predicates];
    const relationships = data.relationships;

    const body = document.createElement("div");
    body.className = "manager";

    const intro = document.createElement("div");
    intro.className = "manager-toolbar";
    const count = document.createElement("p");
    const list = document.createElement("div");
    list.className = "manager-list";

    const createButton = button("New predicate", "primary-button");
    intro.append(count, createButton);
    body.append(intro, list);

    const modal = openModal({
        title: "Manage predicates",
        description: "Create, rename, or change the directionality of reusable relationships.",
        body,
        size: "wide",
    });

    const render = () => {
        count.textContent = `${predicates.length} predicate${predicates.length === 1 ? "" : "s"}`;
        list.replaceChildren();

        if (predicates.length === 0) {
            const empty = document.createElement("div");
            empty.className = "manager-empty";
            empty.textContent = "No predicates yet. Create one to start connecting concepts.";
            list.append(empty);
            return;
        }

        for (const predicate of predicates) {
            list.append(predicateRow(
                predicate,
                relationships,
                current => {
                    openPredicateForm({
                        predicate: current,
                        onSaved: async saved => {
                            predicates = predicates.some(item => item.id === saved.id)
                                ? predicates.map(item => (item.id === saved.id ? saved : item))
                                : [...predicates, saved];
                            render();
                            await onChanged(saved, "updated");
                        },
                    });
                },
                async current => {
                    const affected = relationships.filter(
                        relationship => relationship.predicate_id === current.id,
                    ).length;
                    const confirmed = await confirmDialog({
                        title: "Delete predicate?",
                        message: `Delete “${current.name || "related to"}”?${affected ? ` This will remove ${affected} relationship${affected === 1 ? "" : "s"}.` : ""}`,
                        confirmLabel: "Delete predicate",
                        destructive: true,
                    });
                    if (!confirmed) {
                        return;
                    }

                    try {
                        await api.predicates.remove(current.id);
                        predicates = predicates.filter(item => item.id !== current.id);
                        render();
                        await onChanged(current, "deleted");
                        showToast("Predicate deleted.");
                    } catch (error) {
                        showToast(`Predicate was not deleted. ${displayError(error)}`, "error");
                    }
                },
            ));
        }
    };

    createButton.addEventListener("click", () => {
        openPredicateForm({
            onSaved: async saved => {
                predicates = [...predicates, saved];
                render();
                await onChanged(saved, "created");
            },
        });
    });

    render();
    return modal;
}

export async function openRelationshipForm({
    relationship = null,
    defaultSubjectId = null,
    onSaved,
}) {
    const newPredicateValue = "__new_predicate__";
    let data;
    try {
        data = await api.graph.get();
    } catch (error) {
        showToast(`The relationship form could not load. ${displayError(error)}`, "error");
        return null;
    }

    if (!relationship && data.concepts.length < 2) {
        showToast("Create at least two concepts before adding a relationship.", "error");
        return null;
    }
    if (relationship && !data.relationships.some(item => item.id === relationship.id)) {
        showToast("This relationship no longer exists.", "error");
        return null;
    }

    const conceptOptions = data.concepts
        .map(concept => ({ value: concept.id, label: concept.title }))
        .sort((left, right) => left.label.localeCompare(right.label));
    const predicateOptions = data.predicates
        .map(predicate => ({
            value: predicate.id,
            label: predicateLabel(predicate),
        }))
        .sort((left, right) => left.label.localeCompare(right.label));
    predicateOptions.push({
        value: newPredicateValue,
        label: "Create new predicate...",
    });

    const initialSubject = relationship?.subject_id
        ?? defaultSubjectId
        ?? conceptOptions[0].value;
    const initialPredicate = relationship?.predicate_id
        ?? predicateOptions[0].value;

    return openFormModal({
        title: relationship ? "Edit relationship" : "Create relationship",
        description: "Connect two concepts using an existing predicate or create one here.",
        submitLabel: relationship ? "Save relationship" : "Create relationship",
        fields: [
            {
                name: "subject_id",
                label: "Subject concept",
                type: "select",
                required: true,
                options: conceptOptions,
            },
            {
                name: "predicate_id",
                label: "Predicate",
                type: "select",
                required: true,
                options: predicateOptions,
            },
            {
                name: "new_predicate_name",
                label: "New predicate name",
                placeholder: "For example, depends_on",
                instructions: "Leave blank to create an unnamed predicate.",
                visibleWhen: values => values.predicate_id === newPredicateValue,
            },
            {
                name: "new_predicate_bidirectional",
                label: "Bidirectional",
                type: "checkbox",
                visibleWhen: values => values.predicate_id === newPredicateValue,
            },
            {
                name: "object_id",
                label: "Object concept",
                type: "select",
                required: true,
                options: conceptOptions,
            },
        ],
        initialValues: {
            subject_id: initialSubject,
            predicate_id: initialPredicate,
            new_predicate_name: "",
            new_predicate_bidirectional: true,
            object_id: relationship?.object_id
                ?? conceptOptions.find(option => option.value !== initialSubject)?.value,
        },
        validate: values => (
            values.predicate_id === newPredicateValue
            && !String(values.new_predicate_name ?? "").trim()
            && !values.new_predicate_bidirectional
                ? "An unnamed predicate must be bidirectional."
                : null
        ),
        onSubmit: async values => {
            const payload = {
                subject_id: Number(values.subject_id),
                object_id: Number(values.object_id),
            };
            await assertCurrentGraphReferences([
                {
                    collection: "concepts",
                    id: payload.subject_id,
                    label: "The selected subject concept",
                },
                {
                    collection: "concepts",
                    id: payload.object_id,
                    label: "The selected object concept",
                },
            ]);

            let createdPredicate = null;
            let predicateId;
            if (values.predicate_id === newPredicateValue) {
                createdPredicate = await api.predicates.create({
                    name: optionalText(values.new_predicate_name),
                    bidirectional: Boolean(values.new_predicate_bidirectional),
                });
                predicateId = createdPredicate.id;
            } else {
                predicateId = Number(values.predicate_id);
                await assertCurrentGraphReferences([
                    {
                        collection: "predicates",
                        id: predicateId,
                        label: "The selected predicate",
                    },
                ]);
            }

            try {
                const relationshipPayload = { ...payload, predicate_id: predicateId };
                const saved = relationship
                    ? await api.relationships.update(relationship.id, relationshipPayload)
                    : await api.relationships.create(relationshipPayload);
                await onSaved(saved);
                showToast(
                    createdPredicate
                        ? `Predicate and relationship ${relationship ? "saved" : "created"}.`
                        : `Relationship ${relationship ? "updated" : "created"}.`,
                );
            } catch (error) {
                if (createdPredicate) {
                    try {
                        await api.predicates.remove(createdPredicate.id);
                    } catch {
                        // The original relationship error is more actionable.
                    }
                }
                throw error;
            }
        },
    });
}

export async function deleteRelationship({ relationship, onDeleted, onRefresh }) {
    const confirmed = await confirmDialog({
        title: "Delete relationship?",
        message: "Remove this connection from the knowledge graph? The concepts and predicate will remain.",
        confirmLabel: "Delete relationship",
        destructive: true,
    });
    if (!confirmed) {
        return;
    }

    try {
        await api.relationships.remove(relationship.id);
        await onDeleted?.(relationship);
        showToast("Relationship deleted.");
    } catch (error) {
        await onRefresh?.();
        showToast(`Relationship was not deleted. ${displayError(error)}`, "error");
    }
}

function predicateLabel(predicate) {
    if (!predicate.name) {
        return "related to";
    }
    return predicate.bidirectional
        ? `${predicate.name} (bidirectional)`
        : predicate.name;
}

export async function openMembershipPicker({ project, onSaved }) {
    let data;
    try {
        data = await api.graph.get();
    } catch (error) {
        showToast(`Project concepts could not load. ${displayError(error)}`, "error");
        return null;
    }

    if (!data.projects.some(item => item.id === project.id)) {
        showToast("This project no longer exists.", "error");
        return null;
    }
    if (data.concepts.length === 0) {
        showToast("Create a concept before adding one to this project.", "info");
        return null;
    }

    const currentConceptIds = new Set(
        data.project_concepts
            .filter(membership => membership.project_id === project.id)
            .map(membership => membership.concept_id),
    );
    const available = data.concepts
        .filter(concept => !currentConceptIds.has(concept.id))
        .map(concept => ({ value: concept.id, label: concept.title }))
        .sort((left, right) => left.label.localeCompare(right.label));

    if (available.length === 0) {
        showToast("Every concept is already in this project.", "info");
        return null;
    }

    return openFormModal({
        title: "Add concept to project",
        description: `Choose a concept to add to “${project.title}”.`,
        submitLabel: "Add concept",
        fields: [
            {
                name: "concept_id",
                label: "Concept",
                type: "select",
                required: true,
                options: available,
            },
        ],
        initialValues: {
            concept_id: available[0].value,
        },
        onSubmit: async values => {
            const conceptId = Number(values.concept_id);
            await assertCurrentGraphReferences([
                { collection: "concepts", id: conceptId, label: "The selected concept" },
                { collection: "projects", id: project.id, label: "This project" },
            ]);
            const membership = await api.memberships.create({
                concept_id: conceptId,
                project_id: project.id,
            });
            await onSaved(membership);
            showToast("Concept added to project.");
        },
    });
}

export async function openConceptProjectPicker({ concept, onSaved }) {
    let data;
    try {
        data = await api.graph.get();
    } catch (error) {
        showToast(`Concept projects could not load. ${displayError(error)}`, "error");
        return null;
    }

    if (!data.concepts.some(item => item.id === concept.id)) {
        showToast("This concept no longer exists.", "error");
        return null;
    }
    if (data.projects.length === 0) {
        showToast("Create a project before connecting this concept.", "info");
        return null;
    }

    const currentProjectIds = new Set(
        data.project_concepts
            .filter(membership => membership.concept_id === concept.id)
            .map(membership => membership.project_id),
    );
    const available = data.projects
        .filter(project => !currentProjectIds.has(project.id))
        .map(project => ({ value: project.id, label: project.title }))
        .sort((left, right) => left.label.localeCompare(right.label));

    if (available.length === 0) {
        showToast("This concept is already in every project.", "info");
        return null;
    }

    return openFormModal({
        title: "Add concept to project",
        description: `Choose a project for “${concept.title}”.`,
        submitLabel: "Add to project",
        fields: [
            {
                name: "project_id",
                label: "Project",
                type: "select",
                required: true,
                options: available,
            },
        ],
        initialValues: {
            project_id: available[0].value,
        },
        onSubmit: async values => {
            const projectId = Number(values.project_id);
            await assertCurrentGraphReferences([
                { collection: "concepts", id: concept.id, label: "This concept" },
                { collection: "projects", id: projectId, label: "The selected project" },
            ]);
            const membership = await api.memberships.create({
                concept_id: concept.id,
                project_id: projectId,
            });
            await onSaved(membership);
            showToast("Concept added to project.");
        },
    });
}

export async function openGeneralMembershipForm({ onSaved }) {
    let data;
    try {
        data = await api.graph.get();
    } catch (error) {
        showToast(`Project links could not load. ${displayError(error)}`, "error");
        return null;
    }

    if (data.concepts.length === 0 || data.projects.length === 0) {
        showToast("Create at least one concept and one project first.", "info");
        return null;
    }

    const conceptOptions = data.concepts
        .map(concept => ({ value: concept.id, label: concept.title }))
        .sort((left, right) => left.label.localeCompare(right.label));
    const projectOptions = data.projects
        .map(project => ({ value: project.id, label: project.title }))
        .sort((left, right) => left.label.localeCompare(right.label));

    return openFormModal({
        title: "Connect project and concept",
        description: "Add an existing concept to an existing project.",
        submitLabel: "Create link",
        fields: [
            {
                name: "concept_id",
                label: "Concept",
                type: "select",
                required: true,
                options: conceptOptions,
            },
            {
                name: "project_id",
                label: "Project",
                type: "select",
                required: true,
                options: projectOptions,
            },
        ],
        initialValues: {
            concept_id: conceptOptions[0].value,
            project_id: projectOptions[0].value,
        },
        onSubmit: async values => {
            const conceptId = Number(values.concept_id);
            const projectId = Number(values.project_id);
            await assertCurrentGraphReferences([
                { collection: "concepts", id: conceptId, label: "The selected concept" },
                { collection: "projects", id: projectId, label: "The selected project" },
            ]);
            const membership = await api.memberships.create({
                concept_id: conceptId,
                project_id: projectId,
            });
            await onSaved(membership);
            showToast("Project and concept connected.");
        },
    });
}

export async function removeMembership({
    membership,
    concept,
    project,
    onRemoved,
    onRefresh,
}) {
    const confirmed = await confirmDialog({
        title: "Remove from project?",
        message: `Remove “${concept?.title ?? "this concept"}” from “${project?.title ?? "this project"}”?`,
        confirmLabel: "Remove concept",
        destructive: true,
    });
    if (!confirmed) {
        return;
    }

    try {
        await api.memberships.remove(membership.id);
        await onRemoved?.(membership);
        showToast("Concept removed from project.");
    } catch (error) {
        await onRefresh?.();
        showToast(`Membership was not removed. ${displayError(error)}`, "error");
    }
}
