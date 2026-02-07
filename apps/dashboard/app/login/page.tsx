import { API_BASE_URL } from "@/lib/config";

export default function LoginPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Sign in</h1>
      <p className="text-sm text-muted-foreground">
        Continue to Cognito Hosted UI to sign in.
      </p>
      <a
        className="inline-flex items-center rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground"
        href={`${API_BASE_URL}/v1/login`}
      >
        Sign in with Cognito
      </a>
    </div>
  );
}
