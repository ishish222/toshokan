import { defineConfig } from "orval";

export default defineConfig({
  toshokan: {
    input: {
      target: "../api/openapi/spec.yml",
    },
    output: {
      mode: "tags-split",
      target: "./src/api/generated",
      schemas: "./src/api/generated/model",
      client: "react-query",
      httpClient: "fetch",
      clean: true,
      prettier: true,
      override: {
        mutator: {
          path: "./src/api/client.ts",
          name: "customFetch",
        },
      },
    },
  },
});
