import { NextRequest, NextResponse } from "next/server";
import { refreshTokens } from "@/lib/auth";

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { refresh_token } = body;

        if (!refresh_token) {
            return NextResponse.json(
                { error: "refresh_token is required" },
                { status: 400 }
            );
        }

        const tokens = await refreshTokens(refresh_token);
        return NextResponse.json(tokens);
    } catch (err) {
        console.error("Token refresh error:", err);
        return NextResponse.json(
            { error: "Token refresh failed" },
            { status: 401 }
        );
    }
}
