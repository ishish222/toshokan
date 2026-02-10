"use client";

import {
    createContext,
    useContext,
    useEffect,
    useState,
    type ReactNode,
} from "react";

interface AuthContextType {
    isAuthenticated: boolean;
    isLoading: boolean;
    accessToken: string | null;
    login: () => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

const TOKEN_KEY = "cognito_access_token";
const REFRESH_KEY = "cognito_refresh_token";
const EXPIRY_KEY = "cognito_token_expiry";

export function AuthProvider({ children }: { children: ReactNode }) {
    const [isLoading, setIsLoading] = useState(true);
    const [accessToken, setAccessToken] = useState<string | null>(null);

    useEffect(() => {
        // Check for existing tokens on mount
        const storedToken = localStorage.getItem(TOKEN_KEY);
        const storedExpiry = localStorage.getItem(EXPIRY_KEY);

        if (storedToken && storedExpiry) {
            const expiryTime = parseInt(storedExpiry, 10);
            if (Date.now() < expiryTime) {
                setAccessToken(storedToken);
            } else {
                // Token expired, try refresh
                refreshAccessToken();
                return;
            }
        }
        setIsLoading(false);
    }, []);

    const refreshAccessToken = async () => {
        const refreshToken = localStorage.getItem(REFRESH_KEY);
        if (!refreshToken) {
            clearTokens();
            setIsLoading(false);
            return;
        }

        try {
            const response = await fetch("/api/auth/refresh", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ refresh_token: refreshToken }),
            });

            if (response.ok) {
                const data = await response.json();
                storeTokens(data.access_token, data.expires_in, refreshToken);
                setAccessToken(data.access_token);
            } else {
                clearTokens();
            }
        } catch {
            clearTokens();
        }
        setIsLoading(false);
    };

    const storeTokens = (
        token: string,
        expiresIn: number,
        refreshToken?: string
    ) => {
        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(EXPIRY_KEY, String(Date.now() + expiresIn * 1000));
        if (refreshToken) {
            localStorage.setItem(REFRESH_KEY, refreshToken);
        }
    };

    const clearTokens = () => {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_KEY);
        localStorage.removeItem(EXPIRY_KEY);
        setAccessToken(null);
    };

    const login = () => {
        window.location.href = "/api/auth/login";
    };

    const logout = () => {
        clearTokens();
        window.location.href = "/api/auth/logout";
    };

    // Expose setTokens for callback pages
    useEffect(() => {
        (window as Window & { __setAuthTokens?: typeof storeTokens }).__setAuthTokens = (
            token: string,
            expiresIn: number,
            refreshToken?: string
        ) => {
            storeTokens(token, expiresIn, refreshToken);
            setAccessToken(token);
        };
    }, []);

    return (
        <AuthContext.Provider
            value={{
                isAuthenticated: !!accessToken,
                isLoading,
                accessToken,
                login,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
