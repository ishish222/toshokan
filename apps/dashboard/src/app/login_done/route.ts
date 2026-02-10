import { NextRequest, NextResponse } from "next/server";
import { exchangeCodeForTokens } from "@/lib/auth";

export async function GET(request: NextRequest) {
    const searchParams = request.nextUrl.searchParams;
    const code = searchParams.get("code");
    const error = searchParams.get("error");

    if (error) {
        const errorDescription = searchParams.get("error_description") || error;
        return NextResponse.redirect(
            new URL(`/login?error=${encodeURIComponent(errorDescription)}`, request.url)
        );
    }

    if (!code) {
        return NextResponse.redirect(
            new URL("/login?error=No authorization code received", request.url)
        );
    }

    try {
        const tokens = await exchangeCodeForTokens(code);

        // Redirect to a client page that will store tokens
        const callbackUrl = new URL("/auth/callback", request.url);
        callbackUrl.searchParams.set("access_token", tokens.access_token);
        callbackUrl.searchParams.set("refresh_token", tokens.refresh_token);
        callbackUrl.searchParams.set("expires_in", String(tokens.expires_in));

        return NextResponse.redirect(callbackUrl);
    } catch (err) {
        console.error("Token exchange error:", err);
        return NextResponse.redirect(
            new URL(
                `/login?error=${encodeURIComponent("Authentication failed")}`,
                request.url
            )
        );
    }
}
