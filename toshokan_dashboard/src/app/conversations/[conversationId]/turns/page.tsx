"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useCreateTurn } from "@/lib/api/generated";

const formSchema = z.object({
  text: z.string().min(1),
  input_language: z.string().optional(),
});

type FormValues = z.infer<typeof formSchema>;

export default function CreateTurnPage() {
  const params = useParams<{ conversationId: string }>();
  const conversationId = params.conversationId;
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { text: "", input_language: "ja" },
  });

  const mutation = useCreateTurn();

  const onSubmit = (values: FormValues) => {
    mutation.mutate({
      conversationId,
      data: {
        user_message: {
          text: values.text,
          input_language: values.input_language || undefined,
        },
      },
    });
  };

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Create Turn</h1>
      <Card>
        <CardHeader>
          <CardTitle>New user message</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="text">Message</Label>
              <Textarea id="text" rows={4} {...form.register("text")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="input_language">Input language</Label>
              <Input id="input_language" {...form.register("input_language")} />
            </div>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Sending..." : "Send"}
            </Button>
          </form>
          {mutation.data && (
            <pre className="rounded-md bg-muted p-3 text-xs">
              {JSON.stringify(mutation.data, null, 2)}
            </pre>
          )}
        </CardContent>
      </Card>
    </section>
  );
}
