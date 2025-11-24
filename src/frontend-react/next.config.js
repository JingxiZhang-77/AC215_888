/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Remove standalone output for dev - it's for production builds only
  // output: 'standalone',
  
  // Ensure proper webpack configuration for Docker development
  webpack: (config, { dev, isServer }) => {
    // Disable webpack cache in development to prevent chunk loading issues
    if (dev) {
      config.cache = false;
    }
    return config;
  },
  
  // Set asset prefix to ensure chunks load correctly
  assetPrefix: process.env.NODE_ENV === 'production' ? undefined : '',
}

module.exports = nextConfig
