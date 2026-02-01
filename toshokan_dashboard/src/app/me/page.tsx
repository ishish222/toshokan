"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useGetMe } from "@/lib/api/generated";

export default function MePage() {
  const { data, isLoading, error } = useGetMe();
  const response = data?.status === 200 ? data.data : null;

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Identity</h1>
      <Card>
        <CardHeader>
          <CardTitle>Current user</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {isLoading && <p className="text-sm text-muted-foreground">Loading...</p>}
          {error && (
            <p className="text-sm text-destructive">
              Failed to load profile.
            </p>
          )}
          {data && data.status !== 200 && (
            <pre className="rounded-md bg-muted p-3 text-xs">
              {JSON.stringify(data, null, 2)}
            </pre>
          )}
          {response && (
            <pre className="rounded-md bg-muted p-3 text-xs">
              {JSON.stringify(response, null, 2)}
            </pre>
          )}
        </CardContent>
      </Card>
    </section>
  );
}
