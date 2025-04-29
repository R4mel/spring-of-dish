// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // 모든 IP 허용
    allowedHosts: [
      'chosuncnl.store', // 여기에 허용할 도메인 추가!
      'https://via.placeholder.com/150'
    ]
  }
})
