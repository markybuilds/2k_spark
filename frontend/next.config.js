/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },
  // Set environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
  },
  // GitHub Pages uses a subdirectory based on the repository name
  basePath: process.env.NODE_ENV === 'production' ? '/2k_spark' : '',
  // Set asset prefix for GitHub Pages
  assetPrefix: process.env.NODE_ENV === 'production' ? '/2k_spark' : '',
  // Disable trailing slashes to avoid GitHub Pages redirect issues
  trailingSlash: false,
};

module.exports = nextConfig;
