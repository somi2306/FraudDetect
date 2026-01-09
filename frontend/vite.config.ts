// vite.config.js

import path from "path";
// REMOVED: import tailwindcss from "@tailwindcss/vite"; 
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  // The React plugin is sufficient here. Tailwind should be configured via postcss.config.js
  plugins: [react()], 
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "~": path.resolve(__dirname, "./src"),
    },
  },
});