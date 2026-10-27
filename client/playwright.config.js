import { defineConfig } from '@playwright/test'
import { resolve } from 'node:path'

const python = process.platform === 'win32' ? '../server/.venv/Scripts/python.exe' : '../server/.venv/bin/python'

export default defineConfig({
  testDir: './tests',
  workers: 1,
  fullyParallel: false,
  globalTeardown: './tests/teardown.js',
  use: {
    baseURL: 'http://127.0.0.1:5175',
    browserName: 'chromium',
    channel: process.env.PLAYWRIGHT_CHANNEL || (process.platform === 'win32' ? 'msedge' : undefined),
    reducedMotion: 'reduce',
    screenshot: 'only-on-failure',
    // No traces/videos: evitar almacenar cuerpos de login o cookies de sesión.
    trace: 'off',
    video: 'off',
  },
  webServer: [
    {
      command: `"${resolve(python)}" "${resolve('../server/tests/browser_server.py')}"`,
      cwd: resolve('../server'),
      url: 'http://127.0.0.1:8001/api/health',
      timeout: 60000,
      reuseExistingServer: false,
    },
    {
      command: 'npm run dev -- --host 127.0.0.1 --port 5175 --strictPort',
      url: 'http://127.0.0.1:5175',
      env: { VITE_API_URL: 'http://127.0.0.1:8001' },
      timeout: 60000,
      reuseExistingServer: false,
    },
  ],
})
