"use client";

import Link from "next/link";

import { Button } from "@/components/ui/button";
import { API_BASE_URL } from "@/lib/config";
import AuthStatus from "@/components/auth-status";

export function SiteHeader() {
  return (
    <header className="border-b">
      <div className="container mx-auto flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <span className="text-sm font-semibold">T</span>
          </div>
          <div>
            <p className="text-sm font-semibold">Toshokan API Stubs</p>
            <p className="text-xs text-muted-foreground">
              OpenAPI-driven frontend placeholders
            </p>
          </div>
        </div>
        <nav className="flex items-center gap-2">
          <Button asChild variant="ghost" size="sm">
            <Link href="/">Home</Link>
          </Button>
          <Button asChild variant="secondary" size="sm">
            <Link href="/api-stubs">Endpoints</Link>
          </Button>
          <Button asChild variant="outline" size="sm">
            <Link href="/login">Sign in</Link>
          </Button>
          <Button asChild variant="ghost" size="sm">
            <a href={`${API_BASE_URL}/v1/logout`}>Sign out</a>
          </Button>
          <AuthStatus />
        </nav>
      </div>
    </header>
  );
}
