import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // 모든 IP 허용
    allowedHosts: [
      '' // 여기에 허용할 도메인 추가!
    ]
  }
})
