"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { API_BASE_URL } from "@/lib/config";

type Status = "idle" | "loading" | "success" | "error";

export default function LoginDonePage() {
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    const done = searchParams.get("done");
    if (done === "1") {
      setStatus("success");
      setMessage("Signed in successfully.");
      return;
    }

    const error = searchParams.get("error");
    if (error) {
      setStatus("error");
      setMessage(error);
      return;
    }

    const code = searchParams.get("code");
    const state = searchParams.get("state");
    if (!code || !state) {
      setStatus("error");
      setMessage("Missing authorization code or state.");
      return;
    }

    setStatus("loading");
    const redirectUrl = new URL(`${API_BASE_URL}/v1/login_done`);
    redirectUrl.searchParams.set("code", code);
    redirectUrl.searchParams.set("state", state);
    window.location.href = redirectUrl.toString();
  }, [searchParams]);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Sign-in complete</h1>
      {status === "loading" && (
        <p className="text-sm text-muted-foreground">Finalizing sign-in...</p>
      )}
      {status === "success" && (
        <p className="text-sm text-muted-foreground">{message}</p>
      )}
      {status === "error" && (
        <p className="text-sm text-destructive">{message}</p>
      )}
      <Link
        className="inline-flex items-center rounded-md border px-4 py-2 text-sm font-semibold"
        href="/"
      >
        Back to home
      </Link>
    </div>
  );
}
