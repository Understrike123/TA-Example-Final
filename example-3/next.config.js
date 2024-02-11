/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
}

module.exports = nextConfig

module.exports = {
  webpack: (config) => {
    config.resolve.alias['bokehjs'] = 'bokehjs/build/js/bokeh.min.js';
    return config;
  },
};
