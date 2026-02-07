import Link from "next/link";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiPaths } from "@/lib/openapi";

export default function ApiStubIndexPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold">Endpoint stubs</h1>
        <p className="text-sm text-muted-foreground">
          Each card links to a stubbed UI for the corresponding OpenAPI path.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {apiPaths.map((endpoint) => (
          <Link key={endpoint.id} href={endpoint.exampleRoute}>
            <Card className="h-full transition hover:border-primary/60">
              <CardHeader>
                <CardTitle className="text-base">{endpoint.path}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-muted-foreground">
                <div className="flex flex-wrap items-center gap-2">
                  {endpoint.operations.map((operation) => (
                    <span
                      key={operation.id}
                      className="rounded-full border px-2 py-0.5 text-xs font-semibold uppercase tracking-wide text-foreground"
                    >
                      {operation.method}
                    </span>
                  ))}
                </div>
                <p>{endpoint.operations.length} operation(s)</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
