"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useGetDidascaliaForTurn } from "@/lib/api/generated";

export default function DidascaliaForTurnPage() {
  const [conversationId, setConversationId] = useState("");
  const [turnId, setTurnId] = useState("");
  const [active, setActive] = useState({ conversationId: "", turnId: "" });

  const { data, isLoading } = useGetDidascaliaForTurn(
    active.conversationId,
    active.turnId,
    { query: { enabled: Boolean(active.conversationId && active.turnId) } }
  );
  const response = data?.status === 200 ? data.data : null;

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Didascalia for Turn</h1>
      <Card>
        <CardHeader>
          <CardTitle>Lookup</CardTitle>
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
          <div className="space-y-2">
            <Label htmlFor="turn_id">Turn ID</Label>
            <Input
              id="turn_id"
              value={turnId}
              onChange={(event) => setTurnId(event.target.value)}
            />
          </div>
          <Button onClick={() => setActive({ conversationId, turnId })}>
            Load
          </Button>
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
