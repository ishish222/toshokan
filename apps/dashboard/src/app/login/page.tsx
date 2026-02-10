"use client";

import { Suspense, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { useAuth } from "@/providers/auth-provider";

function LoginContent() {
    const searchParams = useSearchParams();
    const error = searchParams.get("error");
    const { isAuthenticated, isLoading, login } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && isAuthenticated) {
            router.replace("/");
        }
    }, [isLoading, isAuthenticated, router]);

    if (isLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
        );
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                    <CardTitle className="text-2xl">Navigator</CardTitle>
                    <CardDescription>Security testing dashboard</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {error && (
                        <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md">
                            {error}
                        </div>
                    )}
                    <Button onClick={login} className="w-full" size="lg">
                        Sign in with Cognito
                    </Button>
                </CardContent>
            </Card>
        </div>
    );
}

export default function LoginPage() {
    return (
        <Suspense
            fallback={
                <div className="flex min-h-screen items-center justify-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                </div>
            }
        >
            <LoginContent />
        </Suspense>
    );
}
