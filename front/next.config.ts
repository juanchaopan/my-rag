import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  env: {
    CHAT_URL: process.env.CHAT_URL || ""
  }
};

export default nextConfig;
