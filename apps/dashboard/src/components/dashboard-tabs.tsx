"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const tabs = [
  { label: "Daily Goals", href: "/daily-goals" },
  { label: "Account", href: "/account" },
];

export function DashboardTabs() {
  const pathname = usePathname();

  return (
    <div className="border-b border-border bg-card">
      <nav className="px-6 max-w-5xl mx-auto">
        <div className="flex items-end gap-1">
          {tabs.map((tab) => {
            const isActive =
              pathname === tab.href || pathname.startsWith(`${tab.href}/`);
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={`px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${
                  isActive
                    ? "border-primary text-foreground"
                    : "border-transparent text-muted-foreground hover:text-foreground hover:border-warm-300"
                }`}
              >
                {tab.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
