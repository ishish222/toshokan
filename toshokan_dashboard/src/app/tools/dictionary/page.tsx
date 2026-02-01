"use client";

import { zodResolver } from "@hookform/resolvers/zod";
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
import { useDictionaryLookup } from "@/lib/api/generated";

const formSchema = z.object({
  query: z.string().min(1),
  direction: z.enum(["en_to_ja", "ja_to_en"]),
  limit: z.coerce.number().min(1).max(20).default(5),
});

type FormValues = z.infer<typeof formSchema>;

export default function DictionaryPage() {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { query: "", direction: "ja_to_en", limit: 5 },
  });

  const mutation = useDictionaryLookup();

  const onSubmit = (values: FormValues) => {
    mutation.mutate({ data: values });
  };

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Dictionary Lookup</h1>
      <Card>
        <CardHeader>
          <CardTitle>Lookup</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="query">Query</Label>
              <Input id="query" {...form.register("query")} />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Direction</Label>
                <Select
                  value={form.watch("direction")}
                  onValueChange={(value) =>
                    form.setValue("direction", value as "en_to_ja" | "ja_to_en")
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select direction" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ja_to_en">JA → EN</SelectItem>
                    <SelectItem value="en_to_ja">EN → JA</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="limit">Limit</Label>
                <Input id="limit" type="number" {...form.register("limit")} />
              </div>
            </div>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Searching..." : "Search"}
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
