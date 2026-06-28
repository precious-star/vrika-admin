import path from "node:path";
import { fileURLToPath } from "node:url";
import type { NextConfig } from "next";

const appDir = path.dirname(fileURLToPath(import.meta.url));

const nextConfig: NextConfig = {
  output: "standalone",
  turbopack: {
    root: appDir,
  },
  async rewrites() {
    const backendUrl = process.env.INTERNAL_API_URL || "http://admin-api:4000";
    return [
      {
        source: "/be/:path*",
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
