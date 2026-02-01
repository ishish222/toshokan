"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  useGetConversationGoals,
  useUpdateConversationGoals,
} from "@/lib/api/generated";

const formSchema = z.object({
  daily_unit_target: z.coerce.number().min(0).max(500),
});

type FormValues = z.infer<typeof formSchema>;

export default function ConversationGoalsPage() {
  const { data, isLoading } = useGetConversationGoals();
  const response = data?.status === 200 ? data.data : null;

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { daily_unit_target: 0 },
  });

  useEffect(() => {
    if (response) {
      form.reset({ daily_unit_target: response.daily_unit_target });
    }
  }, [response, form]);

  const mutation = useUpdateConversationGoals();

  const onSubmit = (values: FormValues) => {
    mutation.mutate({ data: values });
  };

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Conversation Goals</h1>
      <Card>
        <CardHeader>
          <CardTitle>Current goal</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {isLoading && <p className="text-sm text-muted-foreground">Loading...</p>}
          {data && data.status !== 200 && (
            <pre className="rounded-md bg-muted p-3 text-xs">
              {JSON.stringify(data, null, 2)}
            </pre>
          )}
          {response && (
            <div className="text-sm text-muted-foreground">
              Daily target: <span className="font-medium">{response.daily_unit_target}</span>
            </div>
          )}
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor="daily_unit_target">Daily unit target</Label>
              <Input
                id="daily_unit_target"
                type="number"
                min={0}
                max={500}
                {...form.register("daily_unit_target")}
              />
            </div>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving..." : "Update goal"}
            </Button>
            {mutation.data && (
              <pre className="rounded-md bg-muted p-3 text-xs">
                {JSON.stringify(mutation.data, null, 2)}
              </pre>
            )}
          </form>
        </CardContent>
      </Card>
    </section>
  );
}
