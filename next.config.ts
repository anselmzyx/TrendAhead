import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  cacheComponents: true,
  partialPrefetching: true,
  env: {
    // Inlined at BUILD time (compile-time substitution): "true" only for
    // builds performed on Netlify. Runtime re-renders in serverless
    // functions keep the build's value — reading process.env.NETLIFY
    // directly there fails because it's a build-env-only variable.
    BUILT_ON_NETLIFY: process.env.NETLIFY === "true" ? "true" : "",
  },
  // The generated data/ JSON is read with fs at request time by the dynamic
  // topic fallback; serverless bundlers only trace statically analyzable
  // paths, so include the data files explicitly for every route.
  outputFileTracingIncludes: {
    "/**": ["./data/**"],
  },
  // Simple, well-understood security headers (framework defaults cover the
  // rest; no CSP here — it would need careful tuning to not break Next.js):
  // - nosniff: browsers must not guess content types
  // - DENY: the site has no legitimate iframe-embedding use
  // - referrer policy: send only the origin cross-site
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
