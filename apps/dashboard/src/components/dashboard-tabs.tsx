"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const tabs = [
  { label: "Tests", href: "/tests" },
  { label: "Targets", href: "/targets" },
];

export function DashboardTabs() {
  const pathname = usePathname();

  return (
    <div className="border-b border-slate-800 bg-slate-900/80">
      <nav className="px-6">
        <div className="flex items-end gap-2">
          {tabs.map((tab) => {
            const isActive = pathname === tab.href || pathname.startsWith(`${tab.href}/`);
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={cn(
                  "px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors",
                  isActive
                    ? "border-cyan-400 text-cyan-300"
                    : "border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-600"
                )}
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
