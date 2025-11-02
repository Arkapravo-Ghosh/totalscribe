import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  experimental: {
    // Allow effectively unlimited payloads for Server Actions to support large audio uploads.
    serverActions: {
      bodySizeLimit: Number.MAX_SAFE_INTEGER,
    },
  },
};

export default nextConfig;
