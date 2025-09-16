function ProgressPanel({ tasks, overallProgress, events = [] }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur">
      <h2 className="text-lg font-semibold uppercase tracking-[0.4em] text-slate-200 mb-4">Code AI Task Progress</h2>
      <div className="space-y-4">
        {tasks.map((task) => (
          <div key={task.id ?? task.name}>
            <div className="flex items-center justify-between text-xs uppercase tracking-widest text-slate-300">
              <span>{task.name}</span>
              <span>{task.progress}%</span>
            </div>
            <div className="mt-2 h-3 rounded-full bg-midnight/80 overflow-hidden">
              <div
                className={`h-full rounded-full bg-gradient-to-r from-indigo-500 via-purple-500 to-starlight transition-all duration-500 ease-out ${
                  task.progress >= 100 ? 'animate-pulse-soft' : ''
                }`}
                style={{ width: `${task.progress}%` }}
              />
            </div>
          </div>
        ))}
      </div>
      <div className="mt-6 border-t border-white/10 pt-4">
        <div className="flex items-center justify-between text-xs uppercase tracking-widest text-slate-300">
          <span>Overall Progress</span>
          <span>{overallProgress}%</span>
        </div>
        <div className="mt-2 h-3 rounded-full bg-midnight/80 overflow-hidden">
          <div
            className={`h-full rounded-full bg-gradient-to-r from-teal-400 via-purple-400 to-indigo-500 transition-all duration-500 ease-out ${
              overallProgress >= 100 ? 'animate-pulse-soft' : ''
            }`}
            style={{ width: `${overallProgress}%` }}
          />
        </div>
      </div>
      <div className="mt-6">
        <h3 className="text-xs font-semibold uppercase tracking-[0.4em] text-slate-300 mb-3">Live Task Telemetry</h3>
        <div className="max-h-48 space-y-3 overflow-y-auto pr-1">
          {events.length === 0 && (
            <div className="rounded-xl border border-white/5 bg-midnight/60 px-4 py-3 text-[11px] uppercase tracking-[0.35em] text-slate-400">
              Awaiting inbound progress signals...
            </div>
          )}
          {events.map((event) => (
            <div
              key={event.id}
              className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-xs shadow-inner"
            >
              <div className="flex items-center justify-between font-semibold uppercase tracking-[0.35em] text-slate-200">
                <span>{event.task_name}</span>
                <span>{event.progress}%</span>
              </div>
              {event.note && (
                <p className="mt-2 text-[11px] leading-relaxed text-slate-200/80">{event.note}</p>
              )}
              <div className="mt-2 text-[10px] uppercase tracking-[0.3em] text-slate-400">
                {new Date(event.created_at).toLocaleString()} • {event.source}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ProgressPanel
