import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: {
    host: true,
    port: 5173,
    watch: {
      usePolling: true
    },
    fs: {
      // Permite importar alert_thresholds.json, que vive en la raíz del repo
      // (un nivel por encima de este proyecto), como fuente única de umbrales.
      allow: ['..']
    },
    proxy: {
      '/api/meteogalicia': {
        target: 'https://servizos.meteogalicia.gal',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/meteogalicia/, '')
      }
    }
  }
})
