"use client";

import { zodResolver } from "@hookform/resolvers/zod";
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
import { useSuggestSituation } from "@/lib/api/generated";

const formSchema = z.object({
  formality: z.enum(["formal", "informal"]),
});

type FormValues = z.infer<typeof formSchema>;

export default function SuggestSituationPage() {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { formality: "formal" },
  });

  const mutation = useSuggestSituation();

  const onSubmit = (values: FormValues) => {
    mutation.mutate({ data: values });
  };

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Suggest Situation</h1>
      <Card>
        <CardHeader>
          <CardTitle>Generate suggestion</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
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
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Generating..." : "Suggest"}
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
