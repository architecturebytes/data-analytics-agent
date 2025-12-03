// ui/vite.config.js
// ------------------------------------------------------------------
// CRITICAL: The defineConfig function MUST be imported from 'vite'
import { defineConfig } from 'vite' 
// ------------------------------------------------------------------
import react from '@vitejs/plugin-react'

export default defineConfig({ // Now defineConfig is recognized
  plugins: [react()],
  base: './',
  build: {
    // Corrected path, adjacent to app.py inside the ui folder
    outDir: 'dist_frontend', 
  },
});