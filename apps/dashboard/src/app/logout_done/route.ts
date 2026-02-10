import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
    // After Cognito logout, redirect to home
    return NextResponse.redirect(new URL("/", request.url));
}
