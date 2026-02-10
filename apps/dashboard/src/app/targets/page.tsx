"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { z } from "zod";
import { useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useQueryClient } from "@tanstack/react-query";
import { Header } from "@/components/header";
import { DashboardTabs } from "@/components/dashboard-tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import { useAuth } from "@/providers/auth-provider";
import {
  getGetTargetsQueryKey,
  useGetTargets,
  useDeleteTargetsTargetId,
  usePatchTargetsTargetId,
  usePostTargets,
} from "@/api/generated/targets/targets";

const targetSchema = z.object({
  name: z.string().trim().min(1, "Name is required"),
  seedUris: z
    .array(z.string().trim().url("Enter a valid URI"))
    .min(1, "At least one seed URI is required"),
});

type TargetFormValues = z.infer<typeof targetSchema>;

export default function TargetsPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<"list" | "new">("list");
  const [editingTargetId, setEditingTargetId] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  const { data, isLoading: isTargetsLoading } = useGetTargets(undefined, {
    query: { enabled: isAuthenticated },
  });

  const targets = data?.data?.items ?? [];

  const form = useForm<TargetFormValues>({
    resolver: zodResolver(targetSchema),
    defaultValues: {
      name: "",
      seedUris: [""],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "seedUris",
  });

  useEffect(() => {
    if (fields.length === 0) {
      append("");
    }
  }, [append, fields.length]);

  const createTarget = usePostTargets({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getGetTargetsQueryKey() });
        form.reset({ name: "", seedUris: [""] });
        setActiveTab("list");
      },
    },
  });

  const updateTarget = usePatchTargetsTargetId({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getGetTargetsQueryKey() });
        form.reset({ name: "", seedUris: [""] });
        setEditingTargetId(null);
        setActiveTab("list");
      },
    },
  });

  const deleteTarget = useDeleteTargetsTargetId({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getGetTargetsQueryKey() });
      },
    },
  });

  const onSubmit = (values: TargetFormValues) => {
    if (editingTargetId) {
      updateTarget.mutate({
        targetId: editingTargetId,
        data: {
          name: values.name,
          seed_uris: values.seedUris,
        },
      });
      return;
    }

    createTarget.mutate({
      data: {
        name: values.name,
        seed_uris: values.seedUris,
      },
    });
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <Header />
      <DashboardTabs />
      <main className="p-6">
        <h1 className="text-xl font-semibold text-slate-100 mb-4">Targets</h1>
        <div className="rounded-lg border border-slate-800 bg-slate-900/50">
          <div className="flex items-end gap-2 border-b border-slate-800 px-4 pt-4">
            <button
              type="button"
              onClick={() => setActiveTab("list")}
              className={cn(
                "px-3 py-2 text-sm font-medium border-b-2 -mb-px transition-colors",
                activeTab === "list"
                  ? "border-cyan-400 text-cyan-300"
                  : "border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-600"
              )}
            >
              Target list
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("new")}
              className={cn(
                "px-3 py-2 text-sm font-medium border-b-2 -mb-px transition-colors",
                activeTab === "new"
                  ? "border-cyan-400 text-cyan-300"
                  : "border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-600"
              )}
            >
              New target
            </button>
          </div>

          {activeTab === "list" ? (
            <div className="p-4">
              {isTargetsLoading ? (
                <div className="text-slate-400">Loading targets...</div>
              ) : targets.length === 0 ? (
                <div className="text-slate-400">No targets registered yet.</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow className="border-slate-800">
                      <TableHead className="text-slate-300">Name</TableHead>
                      <TableHead className="text-slate-300">Seed URIs</TableHead>
                      <TableHead className="text-slate-300">Ownership</TableHead>
                      <TableHead className="text-slate-300">Created</TableHead>
                      <TableHead className="text-slate-300 text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {targets.map((target) => {
                      const preview = target.seed_uris.slice(0, 2).join(", ");
                      const remaining = target.seed_uris.length - 2;
                      const seedSummary =
                        remaining > 0 ? `${preview} +${remaining} more` : preview;
                      return (
                        <TableRow key={target.id} className="border-slate-800">
                          <TableCell className="text-slate-200">{target.name}</TableCell>
                          <TableCell className="text-slate-300">{seedSummary}</TableCell>
                          <TableCell className="text-slate-300">
                            {target.ownership_verified ? "Verified" : "Pending"}
                          </TableCell>
                          <TableCell className="text-slate-400">
                            {target.created_at ? new Date(target.created_at).toLocaleString() : "—"}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex items-center justify-end gap-2">
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                  setEditingTargetId(target.id);
                                  form.reset({
                                    name: target.name,
                                    seedUris: target.seed_uris.length > 0 ? target.seed_uris : [""],
                                  });
                                  setActiveTab("new");
                                }}
                                className="border-slate-600 text-slate-100 bg-slate-900/60 hover:bg-slate-800"
                              >
                                Edit
                              </Button>
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => deleteTarget.mutate({ targetId: target.id })}
                                className="border-slate-600 text-slate-100 bg-slate-900/60 hover:bg-slate-800"
                              >
                                Remove
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              )}
            </div>
          ) : (
            <div className="p-4 bg-slate-950/40">
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-slate-200">Name</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="Target name"
                            className="bg-slate-950/60 border-slate-700 text-slate-100 placeholder:text-slate-500"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-200">Seed URIs</span>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => append("")}
                        className="border-slate-500 text-slate-100 bg-slate-900/60 hover:bg-slate-800"
                      >
                        Add URI
                      </Button>
                    </div>

                    <div className="space-y-3 rounded-md border border-slate-800 bg-slate-950/60 p-3">
                      {fields.map((field, index) => (
                        <FormField
                          key={field.id}
                          control={form.control}
                          name={`seedUris.${index}`}
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel className="sr-only">Seed URI {index + 1}</FormLabel>
                              <div className="flex gap-2">
                                <FormControl>
                                  <Input
                                    placeholder="https://example.com"
                                    className="bg-slate-900/80 border-slate-600 text-slate-100 placeholder:text-slate-500"
                                    {...field}
                                  />
                                </FormControl>
                                <Button
                                  type="button"
                                  variant="outline"
                                  size="sm"
                                  onClick={() => remove(index)}
                                  disabled={fields.length <= 1}
                                  className="border-slate-500 text-slate-100 bg-slate-900/60 hover:bg-slate-800"
                                >
                                  Remove
                                </Button>
                              </div>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <Button
                      type="submit"
                      disabled={createTarget.isPending || updateTarget.isPending}
                      className="bg-cyan-600 hover:bg-cyan-500 text-slate-900"
                    >
                      {updateTarget.isPending
                        ? "Saving..."
                        : createTarget.isPending
                          ? "Creating..."
                          : editingTargetId
                            ? "Save"
                            : "Create"}
                    </Button>
                    {createTarget.isError ? (
                      <span className="text-sm text-red-400">Failed to create target.</span>
                    ) : updateTarget.isError ? (
                      <span className="text-sm text-red-400">Failed to save target.</span>
                    ) : null}
                  </div>
                </form>
              </Form>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
