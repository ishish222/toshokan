type DashboardRuntimeConfig = {
  apiBaseUrl?: string;
};

type DashboardConfig = {
  apiBaseUrl: string;
};

let cachedConfig: DashboardConfig | null = null;

function readRuntimeConfig(): DashboardRuntimeConfig | undefined {
  if (typeof window === "undefined") {
    return undefined;
  }
  return (window as Window & { __DASHBOARD_CONFIG__?: DashboardRuntimeConfig })
    .__DASHBOARD_CONFIG__;
}

export function getDashboardConfig(): DashboardConfig {
  if (cachedConfig) {
    return cachedConfig;
  }

  const runtimeConfig = readRuntimeConfig();
  const apiBaseUrl =
    runtimeConfig?.apiBaseUrl ?? process.env.NEXT_PUBLIC_API_URL ?? "";

  cachedConfig = {
    apiBaseUrl,
  };

  return cachedConfig;
}
