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
    return [
      {
        source: '/static/:path*',
        destination: 'http://127.0.0.1:8000/static/:path*',
      },
    ]
  },
}

export default nextConfig