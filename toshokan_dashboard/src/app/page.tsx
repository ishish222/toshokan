export default function Home() {
  return (
    <section className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-semibold">Toshokan Dashboard</h1>
        <p className="text-muted-foreground">
          Basic UI wiring for the Toshokan API endpoints.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <a
          href="/me"
          className="rounded-lg border p-4 transition hover:border-foreground"
        >
          <div className="font-medium">Identity</div>
          <div className="text-sm text-muted-foreground">
            Current user profile.
          </div>
        </a>
        <a
          href="/dashboard"
          className="rounded-lg border p-4 transition hover:border-foreground"
        >
          <div className="font-medium">Dashboard</div>
          <div className="text-sm text-muted-foreground">
            Daily progress and streak.
          </div>
        </a>
        <a
          href="/conversation-goals"
          className="rounded-lg border p-4 transition hover:border-foreground"
        >
          <div className="font-medium">Conversation Goals</div>
          <div className="text-sm text-muted-foreground">
            Module goal settings.
          </div>
        </a>
        <a
          href="/conversations"
          className="rounded-lg border p-4 transition hover:border-foreground"
        >
          <div className="font-medium">Conversations</div>
          <div className="text-sm text-muted-foreground">
            List and manage sessions.
          </div>
        </a>
        <a
          href="/didascalia/latest"
          className="rounded-lg border p-4 transition hover:border-foreground"
        >
          <div className="font-medium">Didascalia</div>
          <div className="text-sm text-muted-foreground">
            Commentary for turns.
          </div>
        </a>
        <a
          href="/tools/dictionary"
          className="rounded-lg border p-4 transition hover:border-foreground"
        >
          <div className="font-medium">Dictionary</div>
          <div className="text-sm text-muted-foreground">
            Word lookup tool.
          </div>
        </a>
      </div>
    </section>
  );
}
