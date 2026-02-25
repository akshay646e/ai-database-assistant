/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*' // Proxy to Backend
      },
      {
        source: '/health',
        destination: 'http://127.0.0.1:8000/health'
      },
      {
        source: '/backend-root',
        destination: 'http://127.0.0.1:8000/'
      }
    ]
  }
}
module.exports = nextConfig
