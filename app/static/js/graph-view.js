import { CONCEPT_PALETTES, PROJECT_PALETTES, toneClass } from "./palette.js";

const NODE_PADDING = 44;
const MAX_NODE_SIZE = 108;

function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

function conceptNodeId(id) {
    return `concept-${id}`;
}

function projectNodeId(id) {
    return `project-${id}`;
}

export class KnowledgeGraphView {
    constructor(container, callbacks = {}) {
        if (typeof window.cytoscape !== "function") {
            throw new Error("Cytoscape could not be loaded.");
        }

        this.callbacks = callbacks;
        this.data = null;
        this.showProjects = false;
        this.selectedId = null;

        this.cy = window.cytoscape({
            container,
            elements: [],
            minZoom: 0.32,
            maxZoom: 2.6,
            boxSelectionEnabled: false,
            autounselectify: true,
            style: this.getStyles(),
        });

        this.bindEvents();
    }

    getStyles() {
        const conceptToneStyles = CONCEPT_PALETTES.map((palette, index) => ({
            selector: `node.concept-tone-${index}`,
            style: {
                "background-fill": "radial-gradient",
                "background-gradient-stop-colors": palette.stops.join(" "),
                "background-gradient-stop-positions": "0% 12% 45% 72% 100%",
                "underlay-color": palette.underlay,
                "underlay-opacity": 0.55,
                "underlay-padding": 7,
                "underlay-shape": "ellipse",
            },
        }));
        const projectToneStyles = PROJECT_PALETTES.map((palette, index) => ({
            selector: `node.project-tone-${index}`,
            style: {
                "background-fill": "radial-gradient",
                "background-gradient-stop-colors": palette.stops.join(" "),
                "background-gradient-stop-positions": "0% 18% 60% 100%",
                "border-color": palette.label,
                "underlay-color": palette.underlay,
                "underlay-opacity": 0.6,
                "underlay-padding": 6,
            },
        }));

        return [
            {
                selector: "node",
                style: {
                    "width": "data(size)",
                    "height": "data(size)",
                    "border-width": 1.2,
                    "border-color": "rgba(215, 231, 255, 0.65)",
                    "label": "data(label)",
                    "color": "#e7edff",
                    "font-family": "Inter, Segoe UI, sans-serif",
                    "font-size": 11,
                    "font-weight": 600,
                    "text-valign": "bottom",
                    "text-halign": "center",
                    "text-margin-y": 9,
                    "text-wrap": "wrap",
                    "text-max-width": 112,
                    "text-background-color": "#050815",
                    "text-background-opacity": 0.74,
                    "text-background-padding": 3,
                    "overlay-opacity": 0,
                    "transition-property": "opacity, border-width, border-color",
                    "transition-duration": "150ms",
                },
            },
            {
                selector: 'node[type = "concept"]',
                style: {
                    "shape": "ellipse",
                },
            },
            {
                selector: 'node[type = "project"]',
                style: {
                    "shape": "round-rectangle",
                    "border-width": 1.5,
                },
            },
            ...conceptToneStyles,
            ...projectToneStyles,
            {
                selector: "edge",
                style: {
                    "width": 1.15,
                    "line-color": "rgba(133, 158, 255, 0.58)",
                    "target-arrow-color": "rgba(143, 189, 255, 0.82)",
                    "target-arrow-shape": "triangle",
                    "target-arrow-fill": "filled",
                    "arrow-scale": 0.82,
                    "curve-style": "bezier",
                    "control-point-step-size": 70,
                    "opacity": 1,
                    "label": "data(label)",
                    "color": "#e7edff",
                    "font-family": "Inter, Segoe UI, sans-serif",
                    "font-size": 8,
                    "text-background-color": "#050815",
                    "text-background-opacity": 0.76,
                    "text-background-padding": 2,
                    "text-rotation": "autorotate",
                    "text-margin-y": -5,
                    "overlay-opacity": 0,
                    "transition-property": "opacity, line-color, width",
                    "transition-duration": "150ms",
                },
            },
            {
                selector: "edge.bidirectional",
                style: {
                    "source-arrow-color": "rgba(143, 189, 255, 0.82)",
                    "source-arrow-shape": "triangle",
                    "source-arrow-fill": "filled",
                },
            },
            {
                selector: "edge.membership",
                style: {
                    "line-color": "rgba(255, 208, 116, 0.4)",
                    "line-style": "dashed",
                    "line-dash-pattern": [1, 5],
                    "target-arrow-shape": "none",
                    "color": "#e7edff",
                    "label": "",
                    "opacity": 1,
                },
            },
            {
                selector: "edge.self-loop",
                style: {
                    "loop-direction": "-45deg",
                    "loop-sweep": "-50deg",
                    "control-point-step-size": 110,
                },
            },
            {
                selector: ".faded",
                style: {
                    "opacity": 0.1,
                },
            },
            {
                selector: "node.search-match",
                style: {
                    "border-color": "#8cecff",
                    "border-width": 3,
                    "underlay-color": "rgba(112, 230, 255, 0.38)",
                    "underlay-opacity": 0.7,
                    "underlay-padding": 10,
                },
            },
            {
                selector: "node:selected",
                style: {
                    "border-color": "#d5f8ff",
                    "border-width": 3,
                    "underlay-color": "rgba(132, 222, 255, 0.42)",
                    "underlay-opacity": 0.75,
                    "underlay-padding": 11,
                },
            },
            {
                selector: "edge:selected",
                style: {
                    "line-color": "#9beeff",
                    "source-arrow-color": "#9beeff",
                    "target-arrow-color": "#9beeff",
                    "opacity": 1,
                    "width": 2.5,
                },
            },
        ];
    }

    bindEvents() {
        this.cy.on("tap", "node", event => {
            const node = event.target;
            this.selectNode(node, true);
        });

        this.cy.on("tap", "edge", event => {
            const edge = event.target;
            if (edge.data("type") === "relationship") {
                this.selectEdge(edge, true);
            }
        });

        this.cy.on("tap", event => {
            if (event.target !== this.cy) {
                return;
            }

            this.clearSelection();
            this.callbacks.onBackgroundTap?.();
        });
    }

    setData(data, { fit = true } = {}) {
        this.data = data;
        const elements = this.buildElements(data);

        this.cy.elements().remove();
        this.cy.add(elements);

        this.arrangeInitialPositions();
        this.cy.layout(this.getLayoutOptions()).run();
        this.applyProjectVisibility();
        this.updateNodeSizes();
        if (fit) {
            this.fit();
        }
    }

    arrangeInitialPositions() {
        const nodes = this.cy.nodes();
        const centerX = this.cy.width() / 2;
        const centerY = this.cy.height() / 2;
        const radius = Math.max(150, nodes.length * 28);

        nodes.forEach((node, index) => {
            const angle = (index / Math.max(nodes.length, 1)) * Math.PI * 2;
            node.position({
                x: centerX + Math.cos(angle) * radius,
                y: centerY + Math.sin(angle) * radius,
            });
        });
    }

    buildElements(data) {
        const conceptIds = new Set(data.concepts.map(concept => concept.id));
        const projectIds = new Set(data.projects.map(project => project.id));
        const predicateById = new Map(
            data.predicates.map(predicate => [predicate.id, predicate]),
        );

        const conceptNodes = data.concepts.map(concept => ({
            group: "nodes",
            classes: toneClass("concept", concept.id),
            data: {
                id: conceptNodeId(concept.id),
                entityId: concept.id,
                type: "concept",
                label: concept.title,
                title: concept.title,
                degree: 0,
                size: NODE_PADDING,
            },
        }));

        const projectNodes = data.projects.map(project => ({
            group: "nodes",
            classes: toneClass("project", project.id),
            data: {
                id: projectNodeId(project.id),
                entityId: project.id,
                type: "project",
                label: project.title,
                title: project.title,
                degree: 0,
                size: NODE_PADDING,
            },
        }));

        const relationshipEdges = data.relationships
            .filter(relationship => (
                conceptIds.has(relationship.subject_id)
                && conceptIds.has(relationship.object_id)
            ))
            .map(relationship => {
                const predicate = predicateById.get(relationship.predicate_id);
                return {
                    group: "edges",
                    classes: [
                        predicate?.bidirectional ? "bidirectional" : "",
                        relationship.subject_id === relationship.object_id ? "self-loop" : "",
                    ].filter(Boolean).join(" "),
                    data: {
                        id: `relationship-${relationship.id}`,
                        entityId: relationship.id,
                        type: "relationship",
                        source: conceptNodeId(relationship.subject_id),
                        target: conceptNodeId(relationship.object_id),
                        label: predicate?.name ?? "",
                        predicateId: relationship.predicate_id,
                    },
                };
            });

        const membershipEdges = data.project_concepts
            .filter(membership => (
                conceptIds.has(membership.concept_id)
                && projectIds.has(membership.project_id)
            ))
            .map(membership => ({
                group: "edges",
                classes: "membership",
                data: {
                    id: `membership-${membership.id}`,
                    entityId: membership.id,
                    type: "membership",
                    source: conceptNodeId(membership.concept_id),
                    target: projectNodeId(membership.project_id),
                    label: "",
                },
            }));

        return [...conceptNodes, ...projectNodes, ...relationshipEdges, ...membershipEdges];
    }

    getLayoutOptions() {
        return {
            name: "cose",
            animate: false,
            fit: true,
            padding: 90,
            randomize: false,
            nodeRepulsion: node => 150000 + Math.max(0, 4 - node.data("degree")) * 22000,
            nodeOverlap: 72,
            componentSpacing: 150,
            idealEdgeLength: 185,
            edgeElasticity: 90,
            gravity: 0.24,
            numIter: 1500,
            initialTemp: 220,
            coolingFactor: 0.94,
            minTemp: 1,
        };
    }

    applyProjectVisibility() {
        this.projectElements().style("display", this.showProjects ? "element" : "none");
    }

    setProjectsVisible(visible, { clearSelection = true, fit = true } = {}) {
        this.showProjects = visible;
        this.applyProjectVisibility();
        this.updateNodeSizes();
        if (clearSelection) {
            this.clearSelection();
        }
        if (fit) {
            this.fit();
        }
    }

    projectElements() {
        return this.cy.elements('[type = "project"], [type = "membership"]');
    }

    visibleElements() {
        return this.showProjects
            ? this.cy.elements()
            : this.cy.elements().not(this.projectElements());
    }

    updateNodeSizes() {
        if (!this.data) {
            return;
        }

        const degrees = new Map();
        const addDegree = id => degrees.set(id, (degrees.get(id) ?? 0) + 1);

        for (const relationship of this.data.relationships) {
            addDegree(`concept-${relationship.subject_id}`);
            addDegree(`concept-${relationship.object_id}`);
        }

        if (this.showProjects) {
            for (const membership of this.data.project_concepts) {
                addDegree(`concept-${membership.concept_id}`);
                addDegree(`project-${membership.project_id}`);
            }
        }

        this.cy.batch(() => {
            this.cy.nodes().forEach(node => {
                const degree = degrees.get(node.id()) ?? 0;
                const size = clamp(
                    NODE_PADDING + Math.sqrt(degree) * 22,
                    NODE_PADDING,
                    MAX_NODE_SIZE,
                );
                node.data("degree", degree);
                node.data("size", size);
            });
        });
    }

    selectEntity(type, entityId) {
        if (type === "project" && !this.showProjects) {
            this.showProjects = true;
            this.applyProjectVisibility();
            this.updateNodeSizes();
        }

        if (type === "relationship") {
            const edge = this.cy.getElementById(`relationship-${entityId}`);
            if (edge.empty()) {
                return false;
            }
            this.selectEdge(edge, true);
            return true;
        }

        const id = type === "project"
            ? projectNodeId(entityId)
            : conceptNodeId(entityId);
        const node = this.cy.getElementById(id);

        if (node.empty()) {
            return false;
        }

        this.selectNode(node, true);
        return true;
    }

    selectNode(node, notify = false) {
        this.cy.elements().unselect();
        this.cy.elements().removeClass("faded");
        this.cy.elements().addClass("faded");

        const neighborhood = node.closedNeighborhood();
        neighborhood.removeClass("faded");
        node.select();
        node.removeClass("search-match");
        this.selectedId = node.id();

        this.cy.animate(
            {
                center: { eles: node },
                zoom: clamp(this.cy.zoom(), 0.8, 1.25),
            },
            { duration: 280 },
        );

        if (notify) {
            this.callbacks.onNodeSelect?.(node.data());
        }
    }

    selectEdge(edge, notify = false) {
        this.cy.elements().unselect();
        this.cy.elements().removeClass("faded");
        this.cy.elements().addClass("faded");

        edge.removeClass("faded");
        edge.connectedNodes().removeClass("faded");
        edge.select();
        this.selectedId = edge.id();

        this.cy.animate(
            {
                center: { eles: edge },
                zoom: clamp(this.cy.zoom(), 0.75, 1.15),
            },
            { duration: 280 },
        );

        if (notify) {
            this.callbacks.onEdgeSelect?.(edge.data());
        }
    }

    clearSelection() {
        if (!this.cy) {
            return;
        }

        this.cy.elements().unselect();
        this.cy.elements().removeClass("faded");
        this.selectedId = null;
    }

    applySearch(query) {
        this.cy.nodes().removeClass("search-match");
        const normalized = query.trim().toLocaleLowerCase();

        if (!normalized) {
            return;
        }

        this.cy.nodes()
            .filter(node => {
                if (node.data("type") === "project" && !this.showProjects) {
                    return false;
                }

                return String(node.data("title")).toLocaleLowerCase().includes(normalized);
            })
            .addClass("search-match");
    }

    fit() {
        if (!this.cy || this.cy.elements().empty()) {
            return;
        }

        const visible = this.visibleElements();
        if (visible.empty()) {
            return;
        }

        this.cy.animate(
            { fit: { eles: visible, padding: 72 } },
            { duration: 260 },
        );
    }

    zoom(direction) {
        const nextZoom = clamp(
            this.cy.zoom() * (direction > 0 ? 1.2 : 0.83),
            this.cy.minZoom(),
            this.cy.maxZoom(),
        );

        this.cy.animate(
            {
                zoom: {
                    level: nextZoom,
                    renderedPosition: {
                        x: this.cy.width() / 2,
                        y: this.cy.height() / 2,
                    },
                },
            },
            { duration: 180 },
        );
    }

    countVisible() {
        return {
            concepts: this.cy.nodes('[type = "concept"]').length,
            projects: this.showProjects ? this.cy.nodes('[type = "project"]').length : 0,
            connections: this.cy.edges('[type = "relationship"]').length,
        };
    }

    destroy() {
        this.cy?.destroy();
        this.cy = null;
    }
}
