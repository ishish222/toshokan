"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useGetDashboard } from "@/lib/api/generated";

const formSchema = z.object({
  start_date: z.string().min(1),
  end_date: z.string().min(1),
});

type FormValues = z.infer<typeof formSchema>;

const formatDate = (value: Date) => value.toISOString().slice(0, 10);
const todayDate = new Date();
const weekAgoDate = new Date();
weekAgoDate.setDate(todayDate.getDate() - 7);
const today = formatDate(todayDate);
const weekAgo = formatDate(weekAgoDate);

export default function DashboardPage() {
  const [params, setParams] = useState<FormValues>({
    start_date: weekAgo,
    end_date: today,
  });

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: params,
  });

  const { data, isLoading, error } = useGetDashboard(params, {
    query: { enabled: Boolean(params.start_date && params.end_date) },
  });

  const response = data?.status === 200 ? data.data : null;

  const onSubmit = (values: FormValues) => {
    setParams(values);
  };

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <Card>
        <CardHeader>
          <CardTitle>Date range</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="grid gap-4 sm:grid-cols-2"
          >
            <div className="space-y-2">
              <Label htmlFor="start_date">Start date</Label>
              <Input id="start_date" type="date" {...form.register("start_date")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="end_date">End date</Label>
              <Input id="end_date" type="date" {...form.register("end_date")} />
            </div>
            <div>
              <Button type="submit">Load</Button>
            </div>
          </form>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Result</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading && <p className="text-sm text-muted-foreground">Loading...</p>}
          {error && (
            <p className="text-sm text-destructive">Failed to load dashboard.</p>
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
