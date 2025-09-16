import { useState } from 'react'

const inputBase =
  'w-full rounded-md bg-midnight/70 border border-starlight/30 px-4 py-2 text-slate-100 focus:outline-none focus:ring-2 focus:ring-starlight focus:border-transparent transition'

function AuthPanel({ config, onLogin, onSignup, loading, error }) {
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    profilePicture: null,
  })

  const handleChange = (event) => {
    const { name, value, files } = event.target
    if (name === 'profilePicture') {
      setForm((prev) => ({ ...prev, profilePicture: files?.[0] ?? null }))
    } else {
      setForm((prev) => ({ ...prev, [name]: value }))
    }
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (mode === 'signup') {
      if (form.password !== form.confirmPassword) {
        alert('Passwords do not match')
        return
      }
      const payload = new FormData()
      payload.append('username', form.username)
      payload.append('email', form.email)
      payload.append('password', form.password)
      if (form.profilePicture) {
        payload.append('profile_picture', form.profilePicture)
      }
      await onSignup(payload)
    } else {
      const payload = new URLSearchParams()
      payload.append('username', form.username)
      payload.append('password', form.password)
      await onLogin(payload)
    }
  }

  const toggleMode = () => {
    setMode((prev) => (prev === 'login' ? 'signup' : 'login'))
    setForm({ username: '', email: '', password: '', confirmPassword: '', profilePicture: null })
  }

  return (
    <div className="w-full max-w-md rounded-2xl bg-white/5 p-8 shadow-glow backdrop-blur-md border border-white/10">
      <div className="text-center mb-6">
        <h1 className="text-5xl font-semibold tracking-[0.4em] text-white drop-shadow-[0_0_15px_rgba(96,63,188,0.75)]">
          {config?.frontend?.title ?? 'Requiem'}
        </h1>
        <p className="mt-3 text-sm text-slate-300 uppercase tracking-[0.4em]">
          {config?.frontend?.subtitle ?? 'The AI That Never Sleeps.'}
        </p>
      </div>
      <div className="flex justify-center gap-4 mb-6">
        <button
          type="button"
          onClick={() => setMode('login')}
          className={`rounded-full px-4 py-2 text-sm uppercase tracking-widest transition shadow ${
            mode === 'login'
              ? 'bg-starlight text-white shadow-glow'
              : 'bg-white/5 text-slate-300 hover:bg-white/10'
          }`}
        >
          Login
        </button>
        <button
          type="button"
          onClick={() => setMode('signup')}
          className={`rounded-full px-4 py-2 text-sm uppercase tracking-widest transition shadow ${
            mode === 'signup'
              ? 'bg-starlight text-white shadow-glow'
              : 'bg-white/5 text-slate-300 hover:bg-white/10'
          }`}
        >
          Sign Up
        </button>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs uppercase tracking-widest text-slate-300 mb-1">Username</label>
          <input
            name="username"
            value={form.username}
            onChange={handleChange}
            className={inputBase}
            placeholder="EternalSeeker"
            required
            minLength={3}
          />
        </div>
        {mode === 'signup' && (
          <div>
            <label className="block text-xs uppercase tracking-widest text-slate-300 mb-1">Email</label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              className={inputBase}
              placeholder="you@requiem.ai"
              required
            />
          </div>
        )}
        <div>
          <label className="block text-xs uppercase tracking-widest text-slate-300 mb-1">Password</label>
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            className={inputBase}
            placeholder="********"
            required
            minLength={8}
          />
        </div>
        {mode === 'signup' && (
          <>
            <div>
              <label className="block text-xs uppercase tracking-widest text-slate-300 mb-1">Confirm Password</label>
              <input
                type="password"
                name="confirmPassword"
                value={form.confirmPassword}
                onChange={handleChange}
                className={inputBase}
                placeholder="********"
                required
                minLength={8}
              />
            </div>
            <div>
              <label className="block text-xs uppercase tracking-widest text-slate-300 mb-1">Profile Picture (optional)</label>
              <input
                type="file"
                name="profilePicture"
                accept="image/*"
                onChange={handleChange}
                className="block w-full text-slate-300"
              />
            </div>
          </>
        )}
        {error && <p className="text-sm text-rose-300 text-center">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-gradient-to-r from-starlight via-purple-600 to-indigo-500 px-4 py-2 text-sm font-semibold uppercase tracking-widest text-white shadow-glow transition hover:scale-[1.02] disabled:opacity-50"
        >
          {loading ? 'Working...' : mode === 'login' ? 'Enter the Portal' : 'Create Account'}
        </button>
        <p className="text-center text-xs text-slate-400">
          {mode === 'login' ? 'No account yet?' : 'Already linked to Requiem?'}{' '}
          <button
            type="button"
            onClick={toggleMode}
            className="text-starlight hover:underline"
          >
            {mode === 'login' ? 'Sign up instead.' : 'Switch to login.'}
          </button>
        </p>
      </form>
    </div>
  )
}

export default AuthPanel
