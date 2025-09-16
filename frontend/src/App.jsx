import { useEffect, useMemo, useState } from 'react'
import AuthPanel from './components/AuthPanel'
import ChatWindow from './components/ChatWindow'
import ProgressPanel from './components/ProgressPanel'

const TOKEN_KEY = 'requiem_token'

const getStoredToken = () => {
  if (typeof window === 'undefined') {
    return null
  }
  return window.localStorage.getItem(TOKEN_KEY)
}

function App() {
  const [config, setConfig] = useState(null)
  const [configError, setConfigError] = useState('')
  const [token, setToken] = useState(getStoredToken)
  const [user, setUser] = useState(null)
  const [tasks, setTasks] = useState([])
  const [overallProgress, setOverallProgress] = useState(0)
  const [messages, setMessages] = useState([])
  const [authLoading, setAuthLoading] = useState(false)
  const [authError, setAuthError] = useState('')
  const [dashboardLoading, setDashboardLoading] = useState(false)
  const [bootstrapError, setBootstrapError] = useState('')

  const apiBaseUrl = useMemo(() => {
    if (config?.api?.base_url) {
      return config.api.base_url
    }
    if (typeof window !== 'undefined') {
      return `${window.location.protocol}//${window.location.host}`
    }
    return 'http://localhost:8000'
  }, [config])

  const buildUrl = (path) => new URL(path, apiBaseUrl).toString()

  const clearSession = () => {
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem(TOKEN_KEY)
    }
    setToken(null)
    setUser(null)
    setTasks([])
    setOverallProgress(0)
    setMessages([])
  }

  useEffect(() => {
    const loadConfig = async () => {
      try {
        const response = await fetch('/config/settings.json', { cache: 'no-store' })
        if (!response.ok) {
          throw new Error('Unable to load shared configuration file.')
        }
        const data = await response.json()
        setConfig(data)
      } catch (error) {
        setConfigError(error.message)
      }
    }
    loadConfig()
  }, [])

  useEffect(() => {
    if (!token || !config) {
      return
    }
    let cancelled = false
    const bootstrap = async () => {
      setDashboardLoading(true)
      setBootstrapError('')
      try {
        await Promise.all([refreshProfile(), refreshProgress(), refreshMessages()])
      } catch (error) {
        if (!cancelled) {
          setBootstrapError(error.message)
        }
      } finally {
        if (!cancelled) {
          setDashboardLoading(false)
        }
      }
    }
    bootstrap()
    return () => {
      cancelled = true
    }
  }, [token, config])

  const authorizedFetch = async (path, options = {}) => {
    const headers = {
      ...(options.headers || {}),
      Authorization: `Bearer ${token}`,
    }
    const response = await fetch(buildUrl(path), { ...options, headers })
    if (response.status === 401) {
      clearSession()
      throw new Error('Session expired. Please log in again.')
    }
    if (!response.ok) {
      const fallback = await response.json().catch(() => ({}))
      throw new Error(fallback.detail || 'Request failed.')
    }
    return response
  }

  const refreshProfile = async () => {
    const response = await authorizedFetch('/auth/me')
    const data = await response.json()
    setUser(data)
  }

  const refreshProgress = async () => {
    const response = await authorizedFetch('/progress/')
    const data = await response.json()
    setTasks(data.tasks ?? [])
    setOverallProgress(Math.round(Number(data.overall_progress ?? 0)))
  }

  const refreshMessages = async () => {
    const response = await authorizedFetch('/chat/history?limit=100')
    const data = await response.json()
    setMessages(data)
  }

  const loginRequest = async (payload) => {
    const response = await fetch(buildUrl('/auth/login'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: payload,
    })
    if (!response.ok) {
      const fallback = await response.json().catch(() => ({}))
      throw new Error(fallback.detail || 'Login failed. Check your credentials.')
    }
    const data = await response.json()
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(TOKEN_KEY, data.access_token)
    }
    setToken(data.access_token)
    setAuthError('')
  }

  const handleLogin = async (payload) => {
    setAuthLoading(true)
    try {
      await loginRequest(payload)
    } catch (error) {
      setAuthError(error.message)
    } finally {
      setAuthLoading(false)
    }
  }

  const handleSignup = async (formData) => {
    setAuthLoading(true)
    setAuthError('')
    try {
      const response = await fetch(buildUrl('/auth/signup'), {
        method: 'POST',
        body: formData,
      })
      if (!response.ok) {
        const fallback = await response.json().catch(() => ({}))
        throw new Error(fallback.detail || 'Unable to create your account.')
      }
      const username = formData.get('username')
      const password = formData.get('password')
      const payload = new URLSearchParams()
      payload.append('username', username)
      payload.append('password', password)
      await loginRequest(payload)
    } catch (error) {
      setAuthError(error.message)
    } finally {
      setAuthLoading(false)
    }
  }

  const handleSendMessage = async (content) => {
    const response = await authorizedFetch('/chat/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    })
    const data = await response.json()
    setMessages((prev) => [...prev, ...data])
    await refreshProgress()
  }

  const handleLogout = () => {
    clearSession()
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-midnight text-slate-100">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(58,12,86,0.55),transparent_55%),radial-gradient(circle_at_80%_0%,rgba(39,67,159,0.35),transparent_55%),radial-gradient(circle_at_50%_100%,rgba(101,25,133,0.4),transparent_60%)]" />
      <div className="absolute inset-0 -z-10 bg-[length:200%_200%] bg-gradient-to-br from-midnight via-[#150a33] to-[#05070d] opacity-90 animate-gradient-flow" />
      <main className="relative z-10 flex min-h-screen flex-col items-center justify-center px-6 py-10">
        {!token && (
          <div className="w-full max-w-6xl flex flex-col items-center gap-10">
            <AuthPanel
              config={config}
              onLogin={handleLogin}
              onSignup={handleSignup}
              loading={authLoading}
              error={authError || configError}
            />
            {configError && (
              <p className="text-sm text-rose-300 text-center max-w-2xl">
                {configError}
              </p>
            )}
          </div>
        )}

        {token && (
          <div className="w-full max-w-6xl space-y-6">
            <header className="flex flex-col gap-4 rounded-2xl border border-white/10 bg-white/5 p-6 shadow-lg backdrop-blur">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h1 className="text-4xl font-semibold uppercase tracking-[0.6em] text-white drop-shadow-[0_0_18px_rgba(96,63,188,0.8)]">
                    {config?.frontend?.title ?? 'Requiem'}
                  </h1>
                  <p className="mt-2 text-sm uppercase tracking-[0.5em] text-slate-300">
                    {config?.frontend?.subtitle ?? 'The AI That Never Sleeps.'}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  {user && (
                    <div className="text-right text-xs uppercase tracking-widest text-slate-300">
                      <p className="text-sm text-slate-100">{user.username}</p>
                      <p>{user.email}</p>
                    </div>
                  )}
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="rounded-full border border-white/20 px-4 py-2 text-xs uppercase tracking-[0.4em] text-slate-200 transition hover:bg-white/10"
                  >
                    Log Out
                  </button>
                </div>
              </div>
              {bootstrapError && (
                <p className="text-sm text-rose-300">
                  {bootstrapError}
                </p>
              )}
              {dashboardLoading && (
                <p className="text-sm text-slate-300">Refreshing the astral data...</p>
              )}
            </header>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-[2fr_1fr]">
              <ChatWindow messages={messages} onSend={handleSendMessage} />
              <ProgressPanel tasks={tasks} overallProgress={overallProgress} />
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
