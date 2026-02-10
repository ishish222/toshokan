"use client";

import { Suspense, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";

declare global {
    interface Window {
        __setAuthTokens?: (
            token: string,
            expiresIn: number,
            refreshToken?: string
        ) => void;
    }
}

function AuthCallbackContent() {
    const searchParams = useSearchParams();
    const router = useRouter();

    useEffect(() => {
        const accessToken = searchParams.get("access_token");
        const refreshToken = searchParams.get("refresh_token");
        const expiresIn = searchParams.get("expires_in");

        if (accessToken && expiresIn) {
            // Store tokens via auth provider
            if (window.__setAuthTokens) {
                window.__setAuthTokens(
                    accessToken,
                    parseInt(expiresIn, 10),
                    refreshToken || undefined
                );
            } else {
                // Fallback: store directly
                localStorage.setItem("cognito_access_token", accessToken);
                localStorage.setItem(
                    "cognito_token_expiry",
                    String(Date.now() + parseInt(expiresIn, 10) * 1000)
                );
                if (refreshToken) {
                    localStorage.setItem("cognito_refresh_token", refreshToken);
                }
            }
        }

        // Redirect to home
        router.replace("/");
    }, [searchParams, router]);

    return (
        <div className="flex min-h-screen items-center justify-center">
            <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                <p className="text-muted-foreground">Completing authentication...</p>
            </div>
        </div>
    );
}

export default function AuthCallbackPage() {
    return (
        <Suspense
            fallback={
                <div className="flex min-h-screen items-center justify-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                </div>
            }
        >
            <AuthCallbackContent />
        </Suspense>
    );
}
