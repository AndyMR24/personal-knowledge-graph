export const CONCEPT_PALETTES = [
    {
        name: "azure",
        stops: ["#f8fbff", "#a6dfff", "#7b87f6", "#493789", "#191136"],
        underlay: "rgba(102, 120, 255, 0.28)",
    },
    {
        name: "violet",
        stops: ["#fff8ff", "#e4c5ff", "#a26bea", "#5b2b8d", "#211238"],
        underlay: "rgba(180, 104, 255, 0.26)",
    },
    {
        name: "teal",
        stops: ["#f5fffd", "#a9f8e8", "#49c9b6", "#176d70", "#0b2630"],
        underlay: "rgba(69, 220, 195, 0.24)",
    },
    {
        name: "rose",
        stops: ["#fff8fa", "#ffc7d9", "#e875a2", "#87365f", "#2e1427"],
        underlay: "rgba(255, 112, 166, 0.24)",
    },
    {
        name: "amber",
        stops: ["#fffdf2", "#ffe6a3", "#eeb85b", "#92602a", "#33200e"],
        underlay: "rgba(255, 198, 92, 0.24)",
    },
    {
        name: "aqua",
        stops: ["#f5feff", "#a7efff", "#52b8da", "#22627c", "#0b2332"],
        underlay: "rgba(81, 211, 244, 0.25)",
    },
];

export const PROJECT_PALETTES = [
    {
        name: "sun",
        stops: ["#fff8d8", "#ffd479", "#c58142", "#56342a"],
        underlay: "rgba(255, 192, 91, 0.24)",
        label: "#ffe9b8",
    },
    {
        name: "ember",
        stops: ["#fff6ef", "#ffb58d", "#de6f56", "#6b302e"],
        underlay: "rgba(255, 128, 91, 0.24)",
        label: "#ffd7c7",
    },
    {
        name: "mint",
        stops: ["#f3fff9", "#a9f2c9", "#4bb883", "#225e47"],
        underlay: "rgba(83, 221, 157, 0.22)",
        label: "#caffdf",
    },
    {
        name: "berry",
        stops: ["#fff6fc", "#f4b6dd", "#bf6ea7", "#5e3157"],
        underlay: "rgba(225, 124, 195, 0.22)",
        label: "#ffd9f0",
    },
    {
        name: "sand",
        stops: ["#fffaf0", "#eed5a7", "#bd9568", "#5b4939"],
        underlay: "rgba(218, 187, 132, 0.22)",
        label: "#f4e2c1",
    },
];

function numericId(id) {
    const parsed = Number(id);
    return Number.isFinite(parsed) ? Math.abs(Math.trunc(parsed)) : 0;
}

export function toneIndex(type, id) {
    const palettes = type === "project" ? PROJECT_PALETTES : CONCEPT_PALETTES;
    return numericId(id) % palettes.length;
}

export function toneClass(type, id) {
    const normalizedType = type === "project" ? "project" : "concept";
    return `${normalizedType}-tone-${toneIndex(normalizedType, id)}`;
}
