/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // Enable standalone output for optimized Docker builds
  output: 'standalone',
  
  // Ensure proper webpack configuration for Docker development
  webpack: (config, { dev, isServer }) => {
    // Disable webpack cache in development to prevent chunk loading issues
    if (dev) {
      config.cache = false;
    }
    
    // Improve module resolution
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      net: false,
      tls: false,
    };
    
    return config;
  },
  
  // Optimize for Docker environment
  swcMinify: true,
  
  // Set proper timeouts for chunk loading
  experimental: {
    optimizeCss: false,
  },
}

module.exports = nextConfig
