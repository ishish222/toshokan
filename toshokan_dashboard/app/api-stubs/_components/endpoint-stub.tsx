import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { apiPaths, getPathById } from "@/lib/openapi";

type EndpointStubProps = {
  pathId: string;
};

export function EndpointStub({ pathId }: EndpointStubProps) {
  const apiPath = getPathById(pathId);

  if (!apiPath) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-semibold">Endpoint not found</h1>
        <p className="text-muted-foreground">
          The stub for this endpoint is missing.
        </p>
        <Button asChild variant="secondary">
          <Link href="/api-stubs">Back to endpoints</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <div className="flex flex-wrap items-center gap-3">
          <span className="font-mono text-sm text-muted-foreground">
            {apiPath.path}
          </span>
        </div>
        <h1 className="text-2xl font-semibold">Endpoint stub</h1>
        <p className="text-sm text-muted-foreground">
          This is a stub view for the API endpoint. Use the placeholders below
          to wire up real requests later.
        </p>
      </div>

      <div className="space-y-6">
        {apiPath.operations.map((operation) => {
          const requestExample = operation.requestExample
            ? JSON.stringify(operation.requestExample, null, 2)
            : "";
          const responseExample = operation.responseExample
            ? JSON.stringify(operation.responseExample, null, 2)
            : "";

          return (
            <div key={operation.id} className="space-y-4">
              <div className="flex flex-wrap items-center gap-3">
                <span className="rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide">
                  {operation.method}
                </span>
                <span className="text-sm font-medium">{operation.summary}</span>
              </div>

              <div className="grid gap-6 lg:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Request</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor={`${operation.id}-api-base`}>
                        API Base URL
                      </Label>
                      <Input
                        id={`${operation.id}-api-base`}
                        placeholder="http://localhost:8000"
                        defaultValue="http://localhost:8000"
                        readOnly
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`${operation.id}-request-body`}>
                        Request body
                      </Label>
                      <Textarea
                        id={`${operation.id}-request-body`}
                        className="min-h-[160px] font-mono text-xs"
                        placeholder="{ }"
                        defaultValue={requestExample}
                      />
                    </div>
                    <Button disabled className="w-full">
                      Send request (stub)
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Response</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <p className="text-sm text-muted-foreground">
                      A successful response will appear here once wired up.
                    </p>
                    <Textarea
                      className="min-h-[220px] font-mono text-xs"
                      placeholder="{ }"
                      defaultValue={responseExample}
                      readOnly
                    />
                  </CardContent>
                </Card>
              </div>
            </div>
          );
        })}
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Other endpoints</h2>
          <Button asChild variant="ghost" size="sm">
            <Link href="/api-stubs">View all</Link>
          </Button>
        </div>
        <div className="flex flex-wrap gap-2">
          {apiPaths.map((item) => (
            <Button
              key={item.id}
              asChild
              variant={item.id === pathId ? "default" : "outline"}
              size="sm"
            >
              <Link href={item.exampleRoute}>{item.path}</Link>
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}
