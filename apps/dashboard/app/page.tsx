import Link from "next/link";

export default function Home() {
  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <p className="text-sm font-medium text-muted-foreground">
          Toshokan API frontend stubs
        </p>
        <h1 className="text-3xl font-semibold">Ready-to-run placeholders</h1>
        <p className="max-w-2xl text-sm text-muted-foreground">
          This app mirrors the OpenAPI surface with minimal UI. Each endpoint
          page contains a stubbed request/response panel and placeholders for
          wiring up live data.
        </p>
      </div>

      <div className="rounded-lg border bg-card p-6">
        <h2 className="text-lg font-semibold">Start exploring</h2>
        <p className="text-sm text-muted-foreground">
          Jump into the endpoints list to see one page per path.
        </p>
        <div className="mt-4">
          <Link
            href="/api-stubs"
            className="inline-flex items-center rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground"
          >
            View endpoints
          </Link>
        </div>
      </div>
    </div>
  );
}
