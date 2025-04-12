import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // TODO: Revert this.
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
