/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
  },
  // GitHub Pages uses a subdirectory, so we need to specify the base path
  // If your repository name is 2k_spark, the basePath should be /2k_spark
  // If you're using a custom domain, you can remove this line
  basePath: process.env.NODE_ENV === 'production' ? '/2k_spark' : '',
  // Disable trailing slashes to avoid GitHub Pages redirect issues
  trailingSlash: false,
};

module.exports = nextConfig;
