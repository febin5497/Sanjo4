import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const apiTarget = process.env.VITE_API_URL || 'https://erp.sanjoconstructions.com'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    open: false,
    proxy: {
      '/api': {
        target: apiTarget,
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path
      },
      '/uploads': {
        target: apiTarget,
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path
      },
      '/static': {
        target: apiTarget,
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path
      }
    }
  }
})
