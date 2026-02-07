"use client";

import { useState } from "react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { API_BASE_URL } from "@/lib/config";
import { apiPaths, getPathById } from "@/lib/openapi";

type EndpointStubProps = {
  pathId: string;
};

export function EndpointStub({ pathId }: EndpointStubProps) {
  const apiPath = getPathById(pathId);
  const [responses, setResponses] = useState<Record<string, string>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [requestBodies, setRequestBodies] = useState<Record<string, string>>(
    {}
  );
  const [queryParams, setQueryParams] = useState<
    Record<string, Record<string, string>>
  >({});

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

          const responseValue = responses[operation.id] ?? responseExample;
          const errorValue = errors[operation.id];
          const isSendableOperation = [
            "getMe",
            "getDashboard",
            "getConversationGoals",
            "updateConversationGoals",
          ].includes(operation.id);
          const requestBodyValue =
            requestBodies[operation.id] ?? requestExample;
          const queryValues =
            queryParams[operation.id] ??
            operation.queryParams?.reduce<Record<string, string>>(
              (acc, param) => {
                acc[param.name] = param.example ?? "";
                return acc;
              },
              {}
            );

          const handleSend = async () => {
            if (!isSendableOperation) {
              return;
            }
            setLoading((prev) => ({ ...prev, [operation.id]: true }));
            setErrors((prev) => ({ ...prev, [operation.id]: "" }));
            try {
              const queryString =
                queryValues && operation.queryParams?.length
                  ? `?${new URLSearchParams(queryValues).toString()}`
                  : "";
              const shouldSendBody = !["GET", "HEAD"].includes(
                operation.method
              );
              const bodyPayload =
                shouldSendBody && requestBodyValue
                  ? JSON.parse(requestBodyValue)
                  : undefined;
              const response = await fetch(
                `${API_BASE_URL}${apiPath.path}${queryString}`,
                {
                  method: operation.method,
                  credentials: "include",
                  headers: shouldSendBody
                    ? { "Content-Type": "application/json" }
                    : undefined,
                  body: shouldSendBody ? JSON.stringify(bodyPayload) : undefined,
                }
              );
              const payload = await response
                .json()
                .catch(() => ({ detail: "Invalid JSON response" }));
              if (!response.ok) {
                throw new Error(payload.detail || "Request failed");
              }
              setResponses((prev) => ({
                ...prev,
                [operation.id]: JSON.stringify(payload, null, 2),
              }));
            } catch (error) {
              const message =
                error instanceof Error ? error.message : "Request failed";
              setErrors((prev) => ({ ...prev, [operation.id]: message }));
            } finally {
              setLoading((prev) => ({ ...prev, [operation.id]: false }));
            }
          };

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
                        placeholder={API_BASE_URL}
                        defaultValue={API_BASE_URL}
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
                        value={requestBodyValue}
                        readOnly={operation.method === "GET"}
                        onChange={(event) =>
                          setRequestBodies((prev) => ({
                            ...prev,
                            [operation.id]: event.target.value,
                          }))
                        }
                      />
                    </div>
                    {operation.queryParams?.length ? (
                      <div className="space-y-3">
                        <p className="text-sm font-medium">Query parameters</p>
                        <div className="grid gap-3">
                          {operation.queryParams.map((param) => (
                            <div key={param.name} className="space-y-1">
                              <Label htmlFor={`${operation.id}-${param.name}`}>
                                {param.name}
                              </Label>
                              <Input
                                id={`${operation.id}-${param.name}`}
                                value={queryValues?.[param.name] ?? ""}
                                onChange={(event) => {
                                  const value = event.target.value;
                                  setQueryParams((prev) => ({
                                    ...prev,
                                    [operation.id]: {
                                      ...(prev[operation.id] ?? {}),
                                      [param.name]: value,
                                    },
                                  }));
                                }}
                              />
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : null}
                    <Button
                      className="w-full"
                      onClick={handleSend}
                      disabled={!isSendableOperation || loading[operation.id]}
                    >
                      {isSendableOperation
                        ? loading[operation.id]
                          ? "Sending..."
                          : "Send request"
                        : "Send request (stub)"}
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
                    {errorValue ? (
                      <p className="text-sm text-destructive">{errorValue}</p>
                    ) : null}
                    <Textarea
                      className="min-h-[220px] font-mono text-xs"
                      placeholder="{ }"
                      value={responseValue}
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
