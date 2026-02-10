import "server-only";

type DashboardServerConfig = {
  cognitoUserPoolId?: string;
  cognitoRegion?: string;
  cognitoClientId?: string;
};

let cachedConfig: DashboardServerConfig | null = null;

export function getServerConfig(): DashboardServerConfig {
  if (cachedConfig) {
    return cachedConfig;
  }

  cachedConfig = {
    cognitoUserPoolId: process.env.COGNITO_USER_POOL_ID,
    cognitoRegion: process.env.COGNITO_REGION,
    cognitoClientId: process.env.COGNITO_CLIENT_ID,
  };

  return cachedConfig;
}
