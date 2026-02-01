"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useUpdateConversationPreferences } from "@/lib/api/generated";

const formSchema = z.object({
  hiragana_hint_enabled: z.enum(["true", "false"]),
});

type FormValues = z.infer<typeof formSchema>;

export default function ConversationPreferencesPage() {
  const params = useParams<{ conversationId: string }>();
  const conversationId = params.conversationId;
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { hiragana_hint_enabled: "false" },
  });

  const mutation = useUpdateConversationPreferences();

  const onSubmit = (values: FormValues) => {
    mutation.mutate({
      conversationId,
      data: { hiragana_hint_enabled: values.hiragana_hint_enabled === "true" },
    });
  };

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Conversation Preferences</h1>
      <Card>
        <CardHeader>
          <CardTitle>Update preferences</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label>Hiragana hints</Label>
              <Select
                value={form.watch("hiragana_hint_enabled")}
                onValueChange={(value) =>
                  form.setValue("hiragana_hint_enabled", value as "true" | "false")
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select preference" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="true">Enabled</SelectItem>
                  <SelectItem value="false">Disabled</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving..." : "Update preferences"}
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
