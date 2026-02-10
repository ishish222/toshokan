"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/header";
import { DashboardTabs } from "@/components/dashboard-tabs";
import { useAuth } from "@/providers/auth-provider";
import { useGetTests } from "@/api/generated/tests/tests";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function TestsPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  const { data, isLoading: isTestsLoading } = useGetTests(undefined, {
    query: { enabled: isAuthenticated },
  });

  const tests = data?.data?.items ?? [];

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
        <h1 className="text-xl font-semibold text-slate-100 mb-4">Tests</h1>
        <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-4">
          {isTestsLoading ? (
            <div className="text-slate-400">Loading tests...</div>
          ) : tests.length === 0 ? (
            <div className="text-slate-400">No tests registered yet.</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-slate-800">
                  <TableHead className="text-slate-300">Test ID</TableHead>
                  <TableHead className="text-slate-300">Target ID</TableHead>
                  <TableHead className="text-slate-300">State</TableHead>
                  <TableHead className="text-slate-300">OWASP</TableHead>
                  <TableHead className="text-slate-300">Created</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {tests.map((test) => (
                  <TableRow key={test.id} className="border-slate-800">
                    <TableCell className="text-slate-200">{test.id}</TableCell>
                    <TableCell className="text-slate-300">{test.target_id}</TableCell>
                    <TableCell className="text-slate-300">{test.state}</TableCell>
                    <TableCell className="text-slate-300">{test.owasp_version}</TableCell>
                    <TableCell className="text-slate-400">
                      {test.created_at ? new Date(test.created_at).toLocaleString() : "—"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </main>
    </div>
  );
}
