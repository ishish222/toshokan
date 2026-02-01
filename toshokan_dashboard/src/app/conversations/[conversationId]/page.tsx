"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useArchiveConversation, useGetConversation, useUpdateConversation } from "@/lib/api/generated";

export default function ConversationDetailPage() {
  const params = useParams<{ conversationId: string }>();
  const conversationId = params.conversationId;
  const [limit, setLimit] = useState(50);
  const [title, setTitle] = useState("");
  const [starred, setStarred] = useState(false);

  const { data, isLoading } = useGetConversation(
    conversationId,
    { limit },
    { query: { enabled: Boolean(conversationId) } }
  );
  const response = data?.status === 200 ? data.data : null;
  const updateMutation = useUpdateConversation();
  const archiveMutation = useArchiveConversation();

  useEffect(() => {
    if (!response) return;
    setTitle(response.title ?? "");
    setStarred(Boolean(response.starred));
  }, [response]);

  return (
    <section className="space-y-4">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold">Conversation</h1>
        <p className="text-sm text-muted-foreground">{conversationId}</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Actions</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Link href={`/conversations/${conversationId}/setup`}>
            <Button variant="outline">Setup</Button>
          </Link>
          <Link href={`/conversations/${conversationId}/preferences`}>
            <Button variant="outline">Preferences</Button>
          </Link>
          <Link href={`/conversations/${conversationId}/turns`}>
            <Button variant="outline">Create Turn</Button>
          </Link>
          <Link href={`/didascalia/latest?conversation_id=${conversationId}`}>
            <Button variant="outline">Latest Didascalia</Button>
          </Link>
          <Button
            variant="destructive"
            onClick={() => archiveMutation.mutate({ conversationId })}
            disabled={archiveMutation.isPending}
          >
            {archiveMutation.isPending ? "Archiving..." : "Archive"}
          </Button>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Update metadata</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-2">
            <Label htmlFor="title">Title</Label>
            <Input
              id="title"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
            />
          </div>
          <div className="flex items-center gap-2">
            <input
              id="starred"
              type="checkbox"
              checked={starred}
              onChange={(event) => setStarred(event.target.checked)}
            />
            <Label htmlFor="starred">Starred</Label>
          </div>
          <Button
            onClick={() =>
              updateMutation.mutate({
                conversationId,
                data: { title, starred },
              })
            }
            disabled={updateMutation.isPending}
          >
            {updateMutation.isPending ? "Saving..." : "Save"}
          </Button>
          {updateMutation.data && (
            <pre className="rounded-md bg-muted p-3 text-xs">
              {JSON.stringify(updateMutation.data, null, 2)}
            </pre>
          )}
          {archiveMutation.data && (
            <pre className="rounded-md bg-muted p-3 text-xs">
              {JSON.stringify(archiveMutation.data, null, 2)}
            </pre>
          )}
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Fetch options</CardTitle>
        </CardHeader>
        <CardContent className="flex items-end gap-4">
          <div className="space-y-2">
            <Label htmlFor="limit">Turns limit</Label>
            <Input
              id="limit"
              type="number"
              min={1}
              max={200}
              value={limit}
              onChange={(event) => setLimit(Number(event.target.value))}
            />
          </div>
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
