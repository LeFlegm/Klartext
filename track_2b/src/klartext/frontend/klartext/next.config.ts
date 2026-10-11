import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/health",
        destination: "http://backend:8000/health",
      },
      {
        source: "/letters",
        destination: "http://backend:8000/letters",
      },
      {
        source: "/documents/:path*",
        destination: "http://backend:8000/documents/:path*",
      },
    ];
  },
};

export default nextConfig;
