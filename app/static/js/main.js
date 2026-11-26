import { api, ApiError } from "./api.js";
import {
    deleteConcept,
    deleteProject,
    deleteRelationship,
    openConceptForm,
    openConceptProjectPicker,
    openGeneralMembershipForm,
    openMembershipPicker,
    openPredicateManager,
    openProjectForm,
    openRelationshipForm,
    removeMembership,
} from "./crud.js";
import { KnowledgeGraphView } from "./graph-view.js";
import { renderMarkdown } from "./markdown.js";
import { toneClass } from "./palette.js";
import { openFormModal, showToast } from "./ui.js";

const OWNER_NAME_KEY = "user.owner-name";

const state = {
    data: null,
    graph: null,
    showProjects: false,
    activeResultIndex: -1,
    searchResults: [],
    selected: null,
};

const dom = {};

function cacheDom() {
    dom.starfield = document.getElementById("starfield");
    dom.brandName = document.getElementById("brand-name");
    dom.ownerNameButton = document.getElementById("owner-name-button");
    dom.searchForm = document.getElementById("search-form");
    dom.searchInput = document.getElementById("graph-search");
    dom.clearSearch = document.getElementById("clear-search");
    dom.searchResults = document.getElementById("search-results");
    dom.createWrap = document.querySelector(".create-wrap");
    dom.createButton = document.getElementById("create-button");
    dom.createMenu = document.getElementById("create-menu");
    dom.projectToggle = document.getElementById("project-toggle");
    dom.projectLegend = document.getElementById("project-legend");
    dom.zoomIn = document.getElementById("zoom-in");
    dom.zoomOut = document.getElementById("zoom-out");
    dom.fitGraph = document.getElementById("fit-graph");
    dom.graphSummary = document.getElementById("graph-summary");
    dom.graphContainer = document.getElementById("cy");
    dom.loading = document.getElementById("graph-loading");
    dom.error = document.getElementById("graph-error");
    dom.errorMessage = document.getElementById("graph-error-message");
    dom.empty = document.getElementById("graph-empty");
    dom.retryLoad = document.getElementById("retry-load");
    dom.detailsPanel = document.getElementById("details-panel");
    dom.detailsContent = document.getElementById("details-content");
    dom.closeDetails = document.getElementById("close-details");
}

function possessiveName(name) {
    const normalized = normalizeOwnerName(name);
    if (!normalized) {
        return "User";
    }
    return normalized.toLocaleLowerCase().endsWith("s")
        ? `${normalized}'`
        : `${normalized}'s`;
}

function normalizeOwnerName(name) {
    return String(name ?? "").replace(/\s+/g, " ").trim();
}

function loadOwnerName() {
    try {
        return normalizeOwnerName(window.localStorage.getItem(OWNER_NAME_KEY));
    } catch {
        return "";
    }
}

function applyOwnerName(name) {
    const normalized = normalizeOwnerName(name);
    const label = possessiveName(normalized);
    dom.brandName.textContent = label;
    dom.ownerNameButton.setAttribute(
        "aria-label",
        normalized ? `Change display name. Currently ${label}.` : "Personalize your display name.",
    );
    document.title = normalized ? `${label} · Knowledge Universe` : "User";
}

function saveOwnerName(name) {
    const normalized = normalizeOwnerName(name);
    try {
        if (normalized) {
            window.localStorage.setItem(OWNER_NAME_KEY, normalized);
        } else {
            window.localStorage.removeItem(OWNER_NAME_KEY);
        }
    } catch {
        throw new Error("The display name could not be saved in this browser.");
    }
    applyOwnerName(normalized);
}

function openOwnerNameForm() {
    openFormModal({
        title: "Personalize your universe",
        description: "Choose the name shown in the header.",
        submitLabel: "Save name",
        fields: [
            {
                name: "name",
                label: "Your name",
                placeholder: "Alice",
                instructions: "Leave blank for default name.",
                maxLength: 80,
            },
        ],
        initialValues: {
            name: loadOwnerName(),
        },
        onSubmit: async values => {
            saveOwnerName(values.name);
            showToast("Display name updated.");
        },
    });
}

function seededRandom(seed) {
    let value = seed;
    return () => {
        value = (value * 16807) % 2147483647;
        return (value - 1) / 2147483646;
    };
}

function createStarfield() {
    const random = seededRandom(104729);
    const fragment = document.createDocumentFragment();

    for (let index = 0; index < 150; index += 1) {
        const star = document.createElement("span");
        const size = 0.6 + random() * 1.7;
        star.className = "star";
        star.style.setProperty("--x", `${(random() * 100).toFixed(2)}%`);
        star.style.setProperty("--y", `${(random() * 100).toFixed(2)}%`);
        star.style.setProperty("--size", `${size.toFixed(2)}px`);
        star.style.setProperty("--opacity", (0.25 + random() * 0.72).toFixed(2));
        star.style.setProperty("--duration", `${(2.8 + random() * 5).toFixed(2)}s`);
        star.style.setProperty("--delay", `${(-random() * 7).toFixed(2)}s`);
        fragment.append(star);
    }

    dom.starfield.replaceChildren(fragment);
}

function normalizeGraphData(data) {
    return {
        concepts: Array.isArray(data?.concepts) ? data.concepts : [],
        predicates: Array.isArray(data?.predicates) ? data.predicates : [],
        relationships: Array.isArray(data?.relationships) ? data.relationships : [],
        projects: Array.isArray(data?.projects) ? data.projects : [],
        project_concepts: Array.isArray(data?.project_concepts) ? data.project_concepts : [],
    };
}

function mountGraph(data) {
    state.graph?.destroy();
    state.graph = new KnowledgeGraphView(dom.graphContainer, {
        onNodeSelect: showNodeDetails,
        onEdgeSelect: showEdgeDetails,
        onBackgroundTap: closeDetails,
    });
    state.graph.setData(data, { fit: true });
}

async function loadGraph() {
    setLoadingState();

    try {
        const data = normalizeGraphData(await api.graph.get());
        state.data = data;
        mountGraph(data);
        updateGraphState();
    } catch (error) {
        showLoadError(error);
    }
}

async function refreshData({ selection = state.selected } = {}) {
    try {
        const desiredSelection = selection ? { ...selection } : null;
        if (desiredSelection?.type === "project" && !state.showProjects) {
            state.showProjects = true;
            dom.projectToggle.checked = true;
        }

        const data = normalizeGraphData(await api.graph.get());
        state.data = data;

        if (!state.graph) {
            mountGraph(data);
        } else {
            state.graph.setData(data, { fit: false });
            state.graph.setProjectsVisible(state.showProjects, {
                clearSelection: false,
                fit: false,
            });
        }

        state.graph.applySearch(dom.searchInput.value);
        updateGraphState();

        const restored = desiredSelection?.id != null
            && state.graph.selectEntity(desiredSelection.type, desiredSelection.id);

        if (!restored) {
            closeDetails();
            state.graph.fit();
        }

        return data;
    } catch (error) {
        showToast(`The graph could not refresh. ${errorMessage(error)}`, "error");
        return null;
    }
}

function errorMessage(error) {
    return error?.message || "The operation could not be completed.";
}

function setLoadingState() {
    dom.loading.hidden = false;
    dom.error.hidden = true;
    dom.empty.hidden = true;
    dom.graphSummary.textContent = "Loading content...";
}

function showLoadError(error) {
    dom.loading.hidden = true;
    dom.empty.hidden = true;
    dom.error.hidden = false;
    dom.graphSummary.textContent = "Map unavailable";

    if (error instanceof ApiError) {
        dom.errorMessage.textContent = error.message;
    } else {
        dom.errorMessage.textContent = error?.message
            || "The graph could not be loaded. Check that the local server is running.";
    }
}

function updateGraphState() {
    dom.loading.hidden = true;
    dom.error.hidden = true;
    updateSummary();

    if (!state.data || (state.data.concepts.length === 0 && state.data.projects.length === 0)) {
        dom.empty.hidden = false;
        closeDetails();
        return;
    }

    dom.empty.hidden = true;
}

function updateSummary() {
    if (!state.data) {
        dom.graphSummary.textContent = "No content loaded";
        return;
    }

    const conceptCount = state.data.concepts.length;
    const projectCount = state.data.projects.length;
    dom.graphSummary.textContent = (
        `${conceptCount} concept${conceptCount === 1 ? "" : "s"}`
        + ` · ${projectCount} project${projectCount === 1 ? "" : "s"}`
    );
    dom.projectLegend.hidden = !state.showProjects;
}

function setProjectVisibility(visible) {
    state.showProjects = visible;
    dom.projectToggle.checked = visible;
    state.graph?.setProjectsVisible(visible);
    updateSummary();

    if (!visible && state.selected?.type === "project") {
        closeDetails();
    }

    if (dom.searchInput.value.trim()) {
        state.graph?.applySearch(dom.searchInput.value);
        renderSearchResults(dom.searchInput.value);
    }
}

function getSearchResults(query) {
    if (!state.data || !query.trim()) {
        return [];
    }

    const normalized = query.trim().toLocaleLowerCase();
    const rank = title => {
        const lower = title.toLocaleLowerCase();
        if (lower === normalized) return 0;
        if (lower.startsWith(normalized)) return 1;
        return 2;
    };

    const concepts = state.data.concepts
        .filter(concept => (
            concept.title.toLocaleLowerCase().includes(normalized)
            || (concept.content ?? "").toLocaleLowerCase().includes(normalized)
        ))
        .map(concept => ({
            type: "concept",
            id: concept.id,
            title: concept.title,
            rank: rank(concept.title),
        }));

    const projects = state.data.projects
        .filter(project => (
            project.title.toLocaleLowerCase().includes(normalized)
            || (project.description ?? "").toLocaleLowerCase().includes(normalized)
        ))
        .map(project => ({
            type: "project",
            id: project.id,
            title: project.title,
            rank: rank(project.title) + 0.25,
        }));

    return [...concepts, ...projects]
        .sort((left, right) => left.rank - right.rank || left.title.localeCompare(right.title))
        .slice(0, 8);
}

function renderSearchResults(query) {
    state.searchResults = getSearchResults(query);
    state.activeResultIndex = -1;
    dom.searchResults.replaceChildren();

    if (!query.trim()) {
        closeSearchResults();
        return;
    }

    if (state.searchResults.length === 0) {
        const empty = document.createElement("div");
        empty.className = "search-empty";
        empty.textContent = "No concepts or projects found.";
        dom.searchResults.append(empty);
        dom.searchResults.hidden = false;
        dom.searchInput.setAttribute("aria-expanded", "true");
        return;
    }

    state.searchResults.forEach((result, index) => {
        const resultButton = document.createElement("button");
        resultButton.type = "button";
        resultButton.className = "search-result";
        resultButton.setAttribute("role", "option");
        resultButton.dataset.index = String(index);

        const orb = document.createElement("span");
        orb.className = [
            "search-result-orb",
            result.type === "project" ? "project" : "",
            toneClass(result.type, result.id),
        ].filter(Boolean).join(" ");
        orb.setAttribute("aria-hidden", "true");

        const copy = document.createElement("span");
        copy.className = "search-result-copy";

        const title = document.createElement("span");
        title.className = "search-result-title";
        title.textContent = result.title;

        const type = document.createElement("span");
        type.className = "search-result-type";
        type.textContent = result.type === "project" ? "Project" : "Concept";

        const hint = document.createElement("span");
        hint.className = "result-hint";
        hint.textContent = "Open";

        copy.append(title, type);
        resultButton.append(orb, copy, hint);
        resultButton.addEventListener("click", () => chooseSearchResult(index));
        dom.searchResults.append(resultButton);
    });

    dom.searchResults.hidden = false;
    dom.searchInput.setAttribute("aria-expanded", "true");
}

function closeSearchResults() {
    dom.searchResults.hidden = true;
    dom.searchInput.setAttribute("aria-expanded", "false");
    state.activeResultIndex = -1;
}

function chooseSearchResult(index) {
    const result = state.searchResults[index];
    if (!result) {
        return;
    }

    if (result.type === "project" && !state.showProjects) {
        setProjectVisibility(true);
    }

    closeSearchResults();
    dom.searchInput.value = result.title;
    dom.clearSearch.hidden = false;
    state.graph?.selectEntity(result.type, result.id);
}

function moveSearchSelection(direction) {
    if (dom.searchResults.hidden || state.searchResults.length === 0) {
        return;
    }

    const items = [...dom.searchResults.querySelectorAll(".search-result")];
    state.activeResultIndex = (
        state.activeResultIndex + direction + items.length
    ) % items.length;

    items.forEach((item, index) => {
        item.classList.toggle("is-active", index === state.activeResultIndex);
        item.setAttribute(
            "aria-selected",
            index === state.activeResultIndex ? "true" : "false",
        );
    });
    items[state.activeResultIndex].scrollIntoView({ block: "nearest" });
}

function clearSearch() {
    dom.searchInput.value = "";
    dom.clearSearch.hidden = true;
    closeSearchResults();
    state.graph?.applySearch("");
    dom.searchInput.focus();
}

function element(tagName, className = "", text = "") {
    const node = document.createElement(tagName);
    if (className) {
        node.className = className;
    }
    if (text) {
        node.textContent = text;
    }
    return node;
}

function actionButton(label, className, onClick) {
    const action = element("button", className, label);
    action.type = "button";
    action.addEventListener("click", onClick);
    return action;
}

function openDetails(type, id, content) {
    state.selected = { type, id };
    dom.detailsContent.replaceChildren(content);
    dom.detailsPanel.classList.add("is-open");
    dom.detailsPanel.setAttribute("aria-hidden", "false");
    dom.detailsContent.scrollTop = 0;
}

function closeDetails() {
    dom.detailsPanel.classList.remove("is-open");
    dom.detailsPanel.setAttribute("aria-hidden", "true");
    state.selected = null;
    state.graph?.clearSelection();
}

function showNodeDetails(nodeData) {
    if (!state.data) {
        return;
    }

    const type = nodeData.type;
    const id = Number(nodeData.entityId);
    const entity = type === "project"
        ? state.data.projects.find(project => project.id === id)
        : state.data.concepts.find(concept => concept.id === id);

    if (!entity) {
        return;
    }

    openDetails(
        type,
        id,
        type === "project"
            ? buildProjectDetails(entity)
            : buildConceptDetails(entity),
    );
}

function showEdgeDetails(edgeData) {
    if (!state.data || edgeData.type !== "relationship") {
        return;
    }

    const id = Number(edgeData.entityId);
    const relationship = state.data.relationships.find(item => item.id === id);
    if (!relationship) {
        return;
    }

    openDetails("relationship", id, buildRelationshipDetails(relationship));
}

function buildDetailHero(type, title, entityId = null, options = {}) {
    const hero = element("div", "detail-hero");
    const orb = element("div", "detail-orb");
    if (type === "relationship") {
        orb.className = "detail-orb relationship-orb";
        orb.textContent = options.bidirectional ? "←→" : "↗";
    } else {
        orb.classList.add(toneClass(type, entityId));
        if (type === "project") {
            orb.classList.add("project");
        }
    }
    orb.setAttribute("aria-hidden", "true");

    const heading = element("div", "detail-heading");
    const typeLabel = element(
        "p",
        "detail-type",
        type === "project" ? "Project" : type === "relationship" ? "Relationship" : "Concept",
    );
    const titleElement = element("h1", "", title);
    heading.append(typeLabel, titleElement);
    hero.append(orb, heading);
    return hero;
}

function buildStat(value, label) {
    const stat = element("div", "stat");
    stat.append(element("strong", "", String(value)), element("span", "", label));
    return stat;
}

function buildDetailActions(onEdit, onDelete) {
    const actions = element("div", "detail-actions");
    actions.append(
        actionButton("Edit", "secondary-button detail-action", onEdit),
        actionButton("Delete", "danger-text-button detail-action", onDelete),
    );
    return actions;
}

function sectionTitle(title, actionLabel = "", onAction = null) {
    const row = element("div", "section-title-row");
    row.append(element("h2", "", title));
    if (actionLabel && onAction) {
        row.append(actionButton(actionLabel, "small-button", onAction));
    }
    return row;
}

function buildConceptDetails(concept) {
    const fragment = document.createDocumentFragment();
    fragment.append(buildDetailHero("concept", concept.title, concept.id));

    const relationships = state.data.relationships.filter(relationship => (
        relationship.subject_id === concept.id || relationship.object_id === concept.id
    ));
    const neighboringIds = new Set(
        relationships.map(relationship => (
            relationship.subject_id === concept.id
                ? relationship.object_id
                : relationship.subject_id
        )),
    );
    const memberships = state.data.project_concepts.filter(
        membership => membership.concept_id === concept.id,
    );

    const stats = element("div", "detail-stats");
    stats.append(
        buildStat(neighboringIds.size, neighboringIds.size === 1 ? "neighbor" : "neighbors"),
        buildStat(memberships.length, memberships.length === 1 ? "project" : "projects"),
    );
    fragment.append(stats);
    fragment.append(buildDetailActions(
        () => openConceptForm({
            concept,
            onSaved: () => saveAndFocus("concept", concept.id),
        }),
        () => deleteConcept({
            concept,
            relationshipCount: relationships.length,
            membershipCount: memberships.length,
            onDeleted: async () => {
                state.selected = null;
                await refreshData({ selection: null });
            },
            onRefresh: () => refreshData({ selection: state.selected }),
        }),
    ));

    const notes = element("section", "detail-section");
    notes.append(element("h2", "", "Field notes"));
    notes.append(concept.content
        ? renderMarkdown(concept.content)
        : element("p", "empty-copy", "No notes recorded yet."));
    fragment.append(notes);

    const connections = element("section", "detail-section");
    connections.append(sectionTitle("Connections", "Add", () => {
        openRelationshipForm({
            defaultSubjectId: concept.id,
            onSaved: saved => saveAndFocus("relationship", saved.id),
        });
    }));
    if (relationships.length === 0) {
        connections.append(element(
            "p",
            "empty-copy",
            "This concept is not connected to anything yet.",
        ));
    } else {
        const list = element("div", "connection-list");
        relationships.forEach(relationship => {
            list.append(buildRelationshipLink(relationship, concept.id));
        });
        connections.append(list);
    }
    fragment.append(connections);

    const projects = element("section", "detail-section");
    projects.append(sectionTitle("Projects", "Add", () => {
        openConceptProjectPicker({
            concept,
            onSaved: () => saveAndFocus("concept", concept.id),
        });
    }));
    if (memberships.length === 0) {
        projects.append(element("p", "empty-copy", "This concept is not in a project yet."));
    } else {
        const list = element("div", "project-list");
        memberships.forEach(membership => {
            const project = state.data.projects.find(
                item => item.id === membership.project_id,
            );
            if (!project) return;

            const row = element("div", "membership-row");
            const link = element("button", "project-chip", project.title);
            link.type = "button";
            link.addEventListener("click", () => {
                if (!state.showProjects) setProjectVisibility(true);
                state.graph?.selectEntity("project", project.id);
            });
            row.append(
                link,
                actionButton("Remove", "small-button small-button-danger", () => {
                    removeMembership({
                        membership,
                        concept,
                        project,
                        onRemoved: () => saveAndFocus("concept", concept.id),
                        onRefresh: () => refreshData({ selection: state.selected }),
                    });
                }),
            );
            list.append(row);
        });
        projects.append(list);
    }
    fragment.append(projects);

    return fragment;
}

function buildRelationshipLink(relationship, currentConceptId) {
    const subject = state.data.concepts.find(
        concept => concept.id === relationship.subject_id,
    );
    const object = state.data.concepts.find(
        concept => concept.id === relationship.object_id,
    );
    const predicate = state.data.predicates.find(
        item => item.id === relationship.predicate_id,
    );
    const other = relationship.subject_id === currentConceptId ? object : subject;
    const direction = relationship.subject_id === currentConceptId ? "Outgoing" : "Incoming";
    const predicateLabel = predicate?.name || "related to";

    const button = element("button", "connection-link");
    button.type = "button";
    const text = element("span", "connection-text");
    text.append(
        element("span", "connection-title", other?.title ?? "Missing concept"),
        element("span", "connection-predicate", `${direction} · ${predicateLabel}`),
    );
    button.append(text, element("span", "connection-arrow", "→"));
    button.addEventListener("click", () => {
        state.graph?.selectEntity("relationship", relationship.id);
    });
    return button;
}

function buildProjectDetails(project) {
    const fragment = document.createDocumentFragment();
    fragment.append(buildDetailHero("project", project.title, project.id));

    const memberships = state.data.project_concepts.filter(
        membership => membership.project_id === project.id,
    );
    const memberIds = new Set(memberships.map(membership => membership.concept_id));
    const neighborIds = new Set();
    for (const relationship of state.data.relationships) {
        const subjectMember = memberIds.has(relationship.subject_id);
        const objectMember = memberIds.has(relationship.object_id);
        if (subjectMember && !objectMember) {
            neighborIds.add(relationship.object_id);
        } else if (objectMember && !subjectMember) {
            neighborIds.add(relationship.subject_id);
        }
    }

    const stats = element("div", "detail-stats");
    stats.append(
        buildStat(neighborIds.size, neighborIds.size === 1 ? "neighbor" : "neighbors"),
        buildStat(memberships.length, memberships.length === 1 ? "concept" : "concepts"),
    );
    fragment.append(stats);
    fragment.append(buildDetailActions(
        () => openProjectForm({
            project,
            onSaved: () => saveAndFocus("project", project.id),
        }),
        () => deleteProject({
            project,
            memberships,
            onDeleted: async () => {
                state.selected = null;
                await refreshData({ selection: null });
            },
            onRefresh: () => refreshData({ selection: state.selected }),
        }),
    ));

    const description = element("section", "detail-section");
    description.append(element("h2", "", "Project brief"));
    description.append(project.description
        ? renderMarkdown(project.description)
        : element("p", "empty-copy", "No project description yet."));
    fragment.append(description);

    const members = element("section", "detail-section");
    members.append(sectionTitle("Concepts", "Add", () => {
        openMembershipPicker({
            project,
            onSaved: () => saveAndFocus("project", project.id),
        });
    }));
    if (memberships.length === 0) {
        members.append(element("p", "empty-copy", "No concepts belong to this project yet."));
    } else {
        const list = element("div", "connection-list");
        memberships.forEach(membership => {
            const concept = state.data.concepts.find(
                item => item.id === membership.concept_id,
            );
            if (!concept) return;

            const row = element("div", "membership-row");
            const view = element("button", "connection-link");
            view.type = "button";
            const text = element("span", "connection-text");
            text.append(
                element("span", "connection-title", concept.title),
                element("span", "connection-predicate", "Project concept"),
            );
            view.append(text, element("span", "connection-arrow", "→"));
            view.addEventListener("click", () => {
                state.graph?.selectEntity("concept", concept.id);
            });

            row.append(
                view,
                actionButton("Remove", "small-button small-button-danger", () => {
                    removeMembership({
                        membership,
                        concept,
                        project,
                        onRemoved: () => saveAndFocus("project", project.id),
                        onRefresh: () => refreshData({ selection: state.selected }),
                    });
                }),
            );
            list.append(row);
        });
        members.append(list);
    }
    fragment.append(members);

    return fragment;
}

function buildRelationshipDetails(relationship) {
    const subject = state.data.concepts.find(
        concept => concept.id === relationship.subject_id,
    );
    const object = state.data.concepts.find(
        concept => concept.id === relationship.object_id,
    );
    const predicate = state.data.predicates.find(
        item => item.id === relationship.predicate_id,
    );
    const fragment = document.createDocumentFragment();
    fragment.append(buildDetailHero(
        "relationship",
        predicate?.name || "related to",
        null,
        { bidirectional: Boolean(predicate?.bidirectional) },
    ));

    fragment.append(buildDetailActions(
        () => openRelationshipForm({
            relationship,
            onSaved: () => saveAndFocus("relationship", relationship.id),
        }),
        () => deleteRelationship({
            relationship,
            onDeleted: () => saveAndFocus("concept", relationship.subject_id),
            onRefresh: () => refreshData({ selection: state.selected }),
        }),
    ));

    const direction = element("section", "detail-section");
    direction.append(element("h2", "", "Connection"));

    const phrase = element("div", "relationship-phrase");
    const subjectButton = actionButton(
        subject?.title ?? "Missing concept",
        "relationship-concept",
        () => state.graph?.selectEntity("concept", relationship.subject_id),
    );
    const predicateLabel = element(
        "span",
        "relationship-predicate",
        predicate.bidirectional ? "←→" : "→",
    );
    const objectButton = actionButton(
        object?.title ?? "Missing concept",
        "relationship-concept",
        () => state.graph?.selectEntity("concept", relationship.object_id),
    );
    phrase.append(subjectButton, predicateLabel, objectButton);
    direction.append(phrase);

    const metadata = element("p", "relationship-meta");
    metadata.textContent = predicate?.bidirectional
        ? "This predicate applies in both directions."
        : "This predicate is directed from subject to object.";
    direction.append(metadata);
    fragment.append(direction);
    return fragment;
}

async function saveAndFocus(type, id) {
    const selection = { type, id };
    if (type === "project") {
        state.showProjects = true;
        dom.projectToggle.checked = true;
    }
    state.selected = selection;
    await refreshData({ selection });
}

function refreshCurrentView() {
    return refreshData({ selection: state.selected });
}

function setCreateMenu(open) {
    dom.createMenu.hidden = !open;
    dom.createButton.setAttribute("aria-expanded", open ? "true" : "false");
}

function handleCreateAction(action) {
    setCreateMenu(false);

    if (action === "concept") {
        openConceptForm({
            onSaved: saved => saveAndFocus("concept", saved.id),
        });
    } else if (action === "project") {
        openProjectForm({
            onSaved: saved => saveAndFocus("project", saved.id),
        });
    } else if (action === "relationship") {
        openRelationshipForm({
            onSaved: saved => saveAndFocus("relationship", saved.id),
        });
    } else if (action === "membership") {
        openGeneralMembershipForm({
            onSaved: membership => saveAndFocus("project", membership.project_id),
        });
    } else if (action === "predicate") {
        openPredicateManager({
            data: state.data,
            onChanged: refreshCurrentView,
        });
    }
}

function bindEvents() {
    dom.retryLoad.addEventListener("click", loadGraph);
    dom.ownerNameButton.addEventListener("click", openOwnerNameForm);
    dom.fitGraph.addEventListener("click", () => state.graph?.fit());
    dom.zoomIn.addEventListener("click", () => state.graph?.zoom(1));
    dom.zoomOut.addEventListener("click", () => state.graph?.zoom(-1));
    dom.closeDetails.addEventListener("click", closeDetails);
    dom.projectToggle.addEventListener("change", event => {
        setProjectVisibility(event.target.checked);
    });

    dom.createButton.addEventListener("click", () => {
        setCreateMenu(dom.createMenu.hidden);
    });
    for (const item of dom.createMenu.querySelectorAll("[data-create]")) {
        item.addEventListener("click", () => handleCreateAction(item.dataset.create));
    }

    dom.searchForm.addEventListener("submit", event => {
        event.preventDefault();
        if (state.activeResultIndex >= 0) {
            chooseSearchResult(state.activeResultIndex);
            return;
        }
        chooseSearchResult(0);
    });

    dom.searchInput.addEventListener("input", event => {
        const query = event.target.value;
        dom.clearSearch.hidden = !query;
        state.graph?.applySearch(query);
        renderSearchResults(query);
    });

    dom.searchInput.addEventListener("focus", () => {
        if (dom.searchInput.value.trim()) {
            renderSearchResults(dom.searchInput.value);
        }
    });

    dom.searchInput.addEventListener("keydown", event => {
        if (event.key === "ArrowDown") {
            event.preventDefault();
            moveSearchSelection(1);
        } else if (event.key === "ArrowUp") {
            event.preventDefault();
            moveSearchSelection(-1);
        } else if (event.key === "Escape") {
            closeSearchResults();
        }
    });

    dom.clearSearch.addEventListener("click", clearSearch);

    document.addEventListener("click", event => {
        if (!dom.searchForm.contains(event.target)) {
            closeSearchResults();
        }
        if (!dom.createWrap.contains(event.target)) {
            setCreateMenu(false);
        }
    });

    document.addEventListener("keydown", event => {
        if (event.key !== "Escape") {
            return;
        }
        if (!dom.createMenu.hidden) {
            setCreateMenu(false);
        } else if (!dom.searchResults.hidden) {
            closeSearchResults();
        } else if (document.getElementById("modal-root").childElementCount === 0) {
            closeDetails();
        }
    });
}

function initialize() {
    cacheDom();
    applyOwnerName(loadOwnerName());
    createStarfield();
    bindEvents();
    loadGraph();
}

initialize();
