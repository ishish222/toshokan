"use client";

import { LogOut, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/providers/auth-provider";
import { useGetMe } from "@/api/generated/user/user";

export function Header() {
  const { logout, isAuthenticated } = useAuth();
  const { data: userData } = useGetMe({
    query: { enabled: isAuthenticated },
  });

  const userEmail = userData?.data?.email ?? "Loading...";

  return (
    <header className="border-b border-border bg-card">
      <div className="flex items-center justify-between px-6 py-3 max-w-5xl mx-auto">
        {/* Logo */}
        <span className="text-lg font-semibold tracking-wide text-foreground">
          toshokan<span className="text-primary">.</span>
        </span>

        {/* Right side */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <User className="h-4 w-4" />
            <span>{userEmail}</span>
          </div>

          <Button
            variant="ghost"
            size="icon"
            onClick={logout}
            className="text-muted-foreground hover:text-foreground h-8 w-8"
          >
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}
