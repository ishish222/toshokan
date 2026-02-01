"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useGetLatestDidascalia } from "@/lib/api/generated";

export default function LatestDidascaliaPage() {
  const searchParams = useSearchParams();
  const initialId = searchParams.get("conversation_id") ?? "";
  const [conversationId, setConversationId] = useState(initialId);
  const [activeId, setActiveId] = useState(initialId);

  useEffect(() => {
    setConversationId(initialId);
    setActiveId(initialId);
  }, [initialId]);

  const { data, isLoading } = useGetLatestDidascalia(activeId, {
    query: { enabled: Boolean(activeId) },
  });
  const response = data?.status === 200 ? data.data : null;

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Latest Didascalia</h1>
        <a
          href="/didascalia/turn"
          className="text-sm text-blue-600 hover:underline"
        >
          Lookup by turn
        </a>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Conversation</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="conversation_id">Conversation ID</Label>
            <Input
              id="conversation_id"
              value={conversationId}
              onChange={(event) => setConversationId(event.target.value)}
            />
          </div>
          <Button onClick={() => setActiveId(conversationId)}>Load</Button>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Result</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading && <p className="text-sm text-muted-foreground">Loading...</p>}
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
