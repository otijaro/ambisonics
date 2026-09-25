/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  typescript: {
    ignoreBuildErrors: true,
  },

  images: {
    unoptimized: true,
  },

  turbopack: {
    root: process.cwd(),
  },

  allowedDevOrigins: [
    'localhost',
    '127.0.0.1',
    '10.248.58.92',
  ],

  async rewrites() {
    return []
  },
}

export default nextConfig