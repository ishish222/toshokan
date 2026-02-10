/**
 * Custom fetch wrapper for orval-generated API hooks.
 * Handles JWT authentication and error responses.
 */

import { getDashboardConfig } from "@/config";

const API_BASE_URL = getDashboardConfig().apiBaseUrl;

const TOKEN_KEY = "cognito_access_token";

/**
 * Get auth token from localStorage
 */
function getAuthToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(TOKEN_KEY);
}

/**
 * Response wrapper matching orval's expected shape
 */
type CustomFetchResponse<T> = T & {
    headers: Headers;
};

/**
 * Custom fetch function for orval.
 * Orval calls this as: customFetch<T>(url, options)
 */
export async function customFetch<T>(
    url: string,
    options?: RequestInit
): Promise<CustomFetchResponse<T>> {
    // Build full URL
    const fullUrl = `${API_BASE_URL}${url}`;

    // Build headers
    const headers = new Headers(options?.headers);

    if (!headers.has("Content-Type") && options?.body) {
        headers.set("Content-Type", "application/json");
    }

    // Add auth token if available
    const token = getAuthToken();
    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetch(fullUrl, {
        ...options,
        headers,
    });

    // Handle auth failures - clear tokens and redirect to login
    if (response.status === 401 || response.status === 403) {
        if (typeof window !== "undefined") {
            // Clear tokens and redirect
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem("cognito_refresh_token");
            localStorage.removeItem("cognito_token_expiry");
            window.location.href = "/api/auth/login";
        }
        throw new Error("Unauthorized");
    }

    // Handle error responses
    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        const error = new Error(
            errorBody.detail || errorBody.title || `HTTP ${response.status}`
        );
        (error as Error & { status: number }).status = response.status;
        throw error;
    }

    // Handle 204 No Content
    if (response.status === 204) {
        return {
            data: undefined,
            status: 204,
            headers: response.headers,
        } as unknown as CustomFetchResponse<T>;
    }

    const data = await response.json();

    // Orval expects response in shape: { data: T, status: number, headers: Headers }
    return {
        data,
        status: response.status,
        headers: response.headers,
    } as unknown as CustomFetchResponse<T>;
}

export default customFetch;
