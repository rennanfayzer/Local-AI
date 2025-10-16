/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  i18n: {
    locales: ['en-US', 'pt-BR'],
    defaultLocale: 'pt-BR',
  },
  webpack: (config) => {
    config.watchOptions.ignored = /node_modules|\\.next|pagefile\\.sys/;
    return config;
  },
};

module.exports = nextConfig;
