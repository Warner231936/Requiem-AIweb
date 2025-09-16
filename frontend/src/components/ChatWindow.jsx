import { useEffect, useRef, useState } from 'react'

function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 shadow-lg backdrop-blur border border-white/10 ${
          isUser
            ? 'bg-gradient-to-r from-purple-600/70 to-indigo-500/70 text-slate-50'
            : 'bg-white/10 text-slate-100'
        }`}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        <span className="mt-2 block text-[10px] uppercase tracking-widest text-slate-300 opacity-70">
          {new Date(message.created_at).toLocaleString()}
        </span>
      </div>
    </div>
  )
}

function ChatWindow({ messages, onSend }) {
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const containerRef = useRef(null)

  useEffect(() => {
    const el = containerRef.current
    if (el) {
      el.scrollTop = el.scrollHeight
    }
  }, [messages])

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!draft.trim()) return
    setSending(true)
    try {
      await onSend(draft)
      setDraft('')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="flex h-full flex-col rounded-2xl border border-white/10 bg-white/5 shadow-xl backdrop-blur">
      <div ref={containerRef} className="flex-1 space-y-4 overflow-y-auto p-6">
        {messages.length === 0 && (
          <div className="text-center text-sm text-slate-400">
            Awaiting your first whisper to awaken Requiem...
          </div>
        )}
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
      </div>
      <form onSubmit={handleSubmit} className="border-t border-white/10 p-4">
        <div className="flex items-end gap-3">
          <textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Speak to the sleepless intelligence..."
            rows={1}
            className="min-h-[56px] flex-1 resize-none rounded-xl bg-midnight/70 px-4 py-3 text-sm text-slate-100 shadow-inner focus:outline-none focus:ring-2 focus:ring-starlight/80"
          />
          <button
            type="submit"
            disabled={sending}
            className="rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 px-5 py-3 text-xs font-semibold uppercase tracking-[0.4em] text-white shadow-glow transition hover:scale-[1.02] disabled:opacity-60"
          >
            {sending ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default ChatWindow
