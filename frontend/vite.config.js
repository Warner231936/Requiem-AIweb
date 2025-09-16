import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const filename = fileURLToPath(import.meta.url)
const baseDir = dirname(filename)
const configPath = resolve(baseDir, '../config/settings.json')

let shared = {}
try {
  const file = readFileSync(configPath, 'utf-8')
  shared = JSON.parse(file)
} catch (error) {
  console.warn('Could not read shared settings.json. Using defaults.', error)
}

const devPort = shared?.frontend?.dev_server_port ?? 5173
const apiBase = shared?.api?.base_url ?? 'http://localhost:8000'

const proxiedPaths = ['/auth', '/chat', '/progress', '/config', '/media']
const proxy = Object.fromEntries(
  proxiedPaths.map((path) => [
    path,
    {
      target: apiBase,
      changeOrigin: true,
      secure: false,
    },
  ]),
)

export default defineConfig({
  plugins: [react()],
  server: {
    port: devPort,
    proxy,
  },
  preview: {
    port: devPort,
  },
})
