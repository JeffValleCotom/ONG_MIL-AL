import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/static/' : '/',
  plugins: [react()],
  build: {
    outDir: '../backend/frontend_dist',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: false,
      },
    },
  },
}))
