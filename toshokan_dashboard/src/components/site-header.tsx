import Link from "next/link";

import { Separator } from "@/components/ui/separator";

const navItems = [
  { href: "/me", label: "Identity" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/conversation-goals", label: "Conversation Goals" },
  { href: "/conversations", label: "Conversations" },
  { href: "/didascalia/latest", label: "Didascalia" },
  { href: "/tools/dictionary", label: "Dictionary" },
];

export default function SiteHeader() {
  return (
    <header className="border-b bg-background">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-6 px-6 py-4">
        <Link href="/" className="text-lg font-semibold">
          Toshokan Dashboard
        </Link>
        <nav className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="transition-colors hover:text-foreground"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
      <Separator />
    </header>
  );
}
