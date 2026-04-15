import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["localhost", "127.0.0.1"],
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "dapulse-res.cloudinary.com",
        pathname: "/image/upload/**",
      },
    ],
  },
};

export default nextConfig;
