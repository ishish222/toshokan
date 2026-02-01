"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useListConversations } from "@/lib/api/generated";

const formSchema = z.object({
  limit: z.coerce.number().min(1).max(100).default(20),
  q: z.string().optional(),
});

type FormValues = z.infer<typeof formSchema>;

export default function ConversationsPage() {
  const [params, setParams] = useState<FormValues>({ limit: 20, q: "" });
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: params,
  });

  const { data, isLoading } = useListConversations(
    {
      limit: params.limit,
      q: params.q || undefined,
    },
    { query: { enabled: true } }
  );

  const response = data?.status === 200 ? data.data : null;

  const onSubmit = (values: FormValues) => {
    setParams(values);
  };

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Conversations</h1>
        <Link href="/conversations/suggest">
          <Button variant="outline">Suggest situation</Button>
        </Link>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="grid gap-4 sm:grid-cols-3"
          >
            <div className="space-y-2">
              <Label htmlFor="limit">Limit</Label>
              <Input id="limit" type="number" {...form.register("limit")} />
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="q">Search</Label>
              <Input id="q" placeholder="Title contains..." {...form.register("q")} />
            </div>
            <div>
              <Button type="submit">Load</Button>
            </div>
          </form>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Results</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading && <p className="text-sm text-muted-foreground">Loading...</p>}
          {data && data.status !== 200 && (
            <pre className="rounded-md bg-muted p-3 text-xs">
              {JSON.stringify(data, null, 2)}
            </pre>
          )}
          {response && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Title</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {response.items?.map((item) => (
                  <TableRow key={item.conversation_id}>
                    <TableCell>{item.title}</TableCell>
                    <TableCell>{item.status ?? "n/a"}</TableCell>
                    <TableCell>
                      <Link
                        className="text-sm text-blue-600 hover:underline"
                        href={`/conversations/${item.conversation_id}`}
                      >
                        Open
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </section>
  );
}
