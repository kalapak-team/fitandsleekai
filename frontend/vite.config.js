import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  server: {
    port: 5173,
    host: "localhost",
    strictPort: true,
    hmr: {
      host: "localhost",
      port: 5173,
      protocol: "ws",
    },
    proxy:
      process.env.VITE_DEV_PROXY_TARGET || process.env.VITE_API_URL || process.env.VITE_API_BASE_URL
        ? {
            "/api": {
              target:
                process.env.VITE_DEV_PROXY_TARGET ||
                process.env.VITE_API_URL ||
                process.env.VITE_API_BASE_URL,
              changeOrigin: true,
              secure: false,
            },
            "/sanctum": {
              target:
                process.env.VITE_DEV_PROXY_TARGET ||
                process.env.VITE_API_URL ||
                process.env.VITE_API_BASE_URL,
              changeOrigin: true,
              secure: false,
            },
          }
        : undefined,
  },
});
