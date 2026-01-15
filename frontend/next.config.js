/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // This tells Vercel: "Build the site even if there are TypeScript errors"
  typescript: {
    ignoreBuildErrors: true,
  },
  // This tells Vercel: "Build the site even if there are ESLint (quote) errors"
  eslint: {
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;