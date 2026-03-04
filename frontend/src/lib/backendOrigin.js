function parseOrigin(input) {
    try {
        return new URL(input);
    } catch {
        return null;
    }
}

function getConfiguredOrigin() {
    const fallback =
        typeof window !== "undefined" && window.location?.origin
            ? window.location.origin
            : "http://127.0.0.1:8000";

    return (
        import.meta.env.VITE_API_URL ||
        import.meta.env.VITE_API_BASE_URL ||
        import.meta.env.VITE_BACKEND_ORIGIN ||
        fallback
    );
}

function normalizeConfiguredOrigin() {
    const configured = getConfiguredOrigin();
    const parsed = parseOrigin(configured);
    if (!parsed) {
        return "http://127.0.0.1:8000";
    }

    return `${parsed.protocol}//${parsed.host}`;
}

export function resolveBackendOrigin() {
    return normalizeConfiguredOrigin();
}

export function resolveApiBaseUrl() {
    const origin = resolveBackendOrigin();
    const trimmed = origin.replace(/\/$/, "");
    return trimmed.endsWith("/api") ? trimmed : `${trimmed}/api`;
}
