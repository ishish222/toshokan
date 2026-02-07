import Link from "next/link";

export default function LogoutDonePage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Signed out</h1>
      <p className="text-sm text-muted-foreground">
        You have been signed out successfully.
      </p>
      <Link
        className="inline-flex items-center rounded-md border px-4 py-2 text-sm font-semibold"
        href="/"
      >
        Back to home
      </Link>
    </div>
  );
}
