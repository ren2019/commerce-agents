// Copyright 2026 Anthropic PBC
// SPDX-License-Identifier: Apache-2.0

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return { beforeFiles: [{ source: "/products/:path*", destination: `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/products/:path*` }] };
  },
  transpilePackages: ["web-shared"],
};

export default nextConfig;
