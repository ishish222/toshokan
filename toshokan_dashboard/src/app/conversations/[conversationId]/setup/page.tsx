"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useParams } from "next/navigation";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  useGetConversationSetup,
  useUpdateConversationSetup,
} from "@/lib/api/generated";

const formSchema = z.object({
  formality: z.enum(["formal", "informal"]).optional(),
  situation: z.string().optional(),
  initiator: z.enum(["system", "user"]).optional(),
  grammar_focus_json: z.string().optional(),
});

type FormValues = z.infer<typeof formSchema>;

export default function ConversationSetupPage() {
  const params = useParams<{ conversationId: string }>();
  const conversationId = params.conversationId;
  const { data } = useGetConversationSetup(conversationId, {
    query: { enabled: Boolean(conversationId) },
  });
  const response = data?.status === 200 ? data.data : null;

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {},
  });

  useEffect(() => {
    if (!response) return;
    form.reset({
      formality: response.formality,
      situation: response.situation,
      initiator: response.initiator,
      grammar_focus_json: response.grammar_focus
        ? JSON.stringify(response.grammar_focus, null, 2)
        : "",
    });
  }, [response, form]);

  const mutation = useUpdateConversationSetup();

  const onSubmit = (values: FormValues) => {
    let grammar_focus;
    if (values.grammar_focus_json) {
      try {
        grammar_focus = JSON.parse(values.grammar_focus_json);
      } catch {
        grammar_focus = undefined;
      }
    }

    mutation.mutate({
      conversationId,
      data: {
        formality: values.formality,
        situation: values.situation,
        initiator: values.initiator,
        grammar_focus,
      },
    });
  };

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Conversation Setup</h1>
      <Card>
        <CardHeader>
          <CardTitle>Edit setup</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Formality</Label>
                <Select
                  value={form.watch("formality")}
                  onValueChange={(value) =>
                    form.setValue("formality", value as "formal" | "informal")
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select formality" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="formal">formal</SelectItem>
                    <SelectItem value="informal">informal</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Initiator</Label>
                <Select
                  value={form.watch("initiator")}
                  onValueChange={(value) =>
                    form.setValue("initiator", value as "system" | "user")
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select initiator" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="system">system</SelectItem>
                    <SelectItem value="user">user</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="situation">Situation</Label>
              <Input id="situation" {...form.register("situation")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="grammar_focus_json">Grammar focus (JSON)</Label>
              <Textarea
                id="grammar_focus_json"
                rows={4}
                placeholder='[{"id":"...","label":"..."}]'
                {...form.register("grammar_focus_json")}
              />
            </div>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving..." : "Update setup"}
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
