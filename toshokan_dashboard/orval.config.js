const path = require("path");

module.exports = {
  toshokan: {
    input: path.resolve(
      __dirname,
      "../toshokan/toshokan_backend/openapi/openapi_bundled.yaml"
    ),
    output: {
      mode: "single",
      target: "src/lib/api/generated.ts",
      schemas: "src/lib/api/model",
      client: "react-query",
      override: {
        mutator: {
          path: "src/lib/api/fetcher.ts",
          name: "customFetch",
        },
      },
    },
  },
};
