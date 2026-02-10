"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/header";
import { DashboardTabs } from "@/components/dashboard-tabs";
import { useAuth } from "@/providers/auth-provider";
import { useGetMe } from "@/api/generated/user/user";
import { useGetCustomer } from "@/api/generated/customer/customer";

function Field({ label, value }: { label: string; value?: string | null }) {
  return (
    <div>
      <dt className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
        {label}
      </dt>
      <dd className="mt-1 text-sm text-foreground">{value || "—"}</dd>
    </div>
  );
}

export default function AccountPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  const { data: userData, isLoading: isUserLoading } = useGetMe({
    query: { enabled: isAuthenticated },
  });
  const { data: customerData, isLoading: isCustomerLoading } = useGetCustomer({
    query: { enabled: isAuthenticated },
  });

  const user = userData?.data;
  const customer = customerData?.data;

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const isDataLoading = isUserLoading || isCustomerLoading;

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <DashboardTabs />

      <main className="px-6 py-8 max-w-3xl mx-auto space-y-6">
        {isDataLoading ? (
          <p className="text-sm text-muted-foreground">Loading account...</p>
        ) : (
          <>
            {/* ---- User section ---- */}
            <section className="rounded-xl border border-border bg-card p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-foreground mb-4">
                Profile
              </h2>
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4">
                <Field label="Email" value={user?.email} />
                <Field label="Timezone" value={user?.timezone} />
                <Field
                  label="Roles"
                  value={user?.roles?.join(", ") || "None"}
                />
                <Field
                  label="Member since"
                  value={
                    user?.created_at
                      ? new Date(user.created_at).toLocaleDateString()
                      : undefined
                  }
                />
              </dl>
            </section>

            {/* ---- Customer / Organisation section ---- */}
            <section className="rounded-xl border border-border bg-card p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-foreground mb-4">
                Organisation
              </h2>
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4">
                <Field label="Name" value={customer?.name} />
                <Field label="Contact email" value={customer?.contact?.email} />
                <Field label="Phone" value={customer?.contact?.phone} />
                <Field
                  label="Tokens"
                  value={
                    customer?.tokens != null
                      ? customer.tokens.toLocaleString()
                      : undefined
                  }
                />
                <Field
                  label="Created"
                  value={
                    customer?.created_at
                      ? new Date(customer.created_at).toLocaleDateString()
                      : undefined
                  }
                />
              </dl>
            </section>
          </>
        )}
      </main>
    </div>
  );
}
