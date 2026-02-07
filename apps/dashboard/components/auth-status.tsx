"use client";

import { useEffect, useState } from "react";

import { API_BASE_URL } from "@/lib/config";

type AuthState = {
  status: "loading" | "authenticated" | "unauthenticated";
  email?: string;
};

export default function AuthStatus(): JSX.Element | null {
  const [state, setState] = useState<AuthState>({ status: "loading" });

  useEffect(() => {
    fetch(`${API_BASE_URL}/v1/me`, { credentials: "include" })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error("Not authenticated");
        }
        const payload = await response.json();
        setState({ status: "authenticated", email: payload.email });
      })
      .catch(() => {
        setState({ status: "unauthenticated" });
      });
  }, []);

  if (state.status === "loading") {
    return <span className="text-xs text-muted-foreground">Checking...</span>;
  }

  if (state.status === "authenticated") {
    return (
      <span className="text-xs text-muted-foreground">{state.email}</span>
    );
  }

  return null;
}
