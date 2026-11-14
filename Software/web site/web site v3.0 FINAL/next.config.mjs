/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  typescript: {
    ignoreBuildErrors: true,
  },

  images: {
    unoptimized: true,
  },

  allowedDevOrigins: [
    'localhost',
    '127.0.0.1',
  ],

  async rewrites() {
    return []
  },
}

export default nextConfig
