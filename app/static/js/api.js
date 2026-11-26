const JSON_HEADERS = {
    Accept: "application/json",
    "Content-Type": "application/json",
};

export class ApiError extends Error {
    constructor(message, status, payload = null) {
        super(message);
        this.name = "ApiError";
        this.status = status;
        this.payload = payload;
    }
}

function describeDetail(detail) {
    if (typeof detail === "string") {
        return detail;
    }

    if (Array.isArray(detail)) {
        return detail
            .map(item => item?.msg ?? String(item))
            .join("; ");
    }

    return detail ? JSON.stringify(detail) : "";
}

async function request(path, options = {}) {
    const response = await fetch(path, {
        method: options.method ?? "GET",
        headers: {
            Accept: JSON_HEADERS.Accept,
            ...(options.body === undefined ? {} : { "Content-Type": JSON_HEADERS["Content-Type"] }),
            ...options.headers,
        },
        body: options.body === undefined ? undefined : JSON.stringify(options.body),
    });

    if (!response.ok) {
        let payload = null;
        const contentType = response.headers.get("content-type") ?? "";

        try {
            payload = contentType.includes("application/json")
                ? await response.json()
                : await response.text();
        } catch {
            payload = null;
        }

        const detail = payload && typeof payload === "object" ? payload.detail : payload;
        const serverMessage = describeDetail(detail);
        const message = (
            serverMessage && serverMessage !== "Internal Server Error"
                ? serverMessage
                : response.status >= 500
                    ? "The server could not complete the request. A referenced item may no longer exist."
                    : `The server returned HTTP ${response.status}.`
        );

        throw new ApiError(message, response.status, payload);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}

function withQuery(path, query) {
    if (!query) {
        return path;
    }

    return `${path}?${new URLSearchParams({ title: query }).toString()}`;
}

const resource = basePath => ({
    list: query => request(withQuery(`${basePath}/`, query)),
    get: id => request(`${basePath}/${encodeURIComponent(id)}`),
    create: data => request(`${basePath}/`, { method: "POST", body: data }),
    update: (id, data) => request(`${basePath}/${encodeURIComponent(id)}`, {
        method: "PATCH",
        body: data,
    }),
    remove: id => request(`${basePath}/${encodeURIComponent(id)}`, { method: "DELETE" }),
});

export const api = {
    graph: {
        get: () => request("/graph/"),
        neighborhood: conceptId => request(
            `/concepts/${encodeURIComponent(conceptId)}/neighborhood`,
        ),
    },
    concepts: resource("/concepts"),
    predicates: resource("/predicates"),
    relationships: resource("/relationships"),
    projects: resource("/projects"),
    memberships: {
        list: () => request("/project_concepts/"),
        get: id => request(`/project_concepts/${encodeURIComponent(id)}`),
        create: data => request("/project_concepts/", { method: "POST", body: data }),
        remove: id => request(
            `/project_concepts/${encodeURIComponent(id)}`,
            { method: "DELETE" },
        ),
    },
};
