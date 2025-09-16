const formatDuration = (seconds) => {
  if (seconds === null || seconds === undefined) {
    return '—'
  }
  if (seconds < 60) {
    return `${Math.round(seconds)}s`
  }
  const minutes = Math.floor(seconds / 60)
  const remainder = Math.round(seconds % 60)
  if (minutes < 60) {
    return `${minutes}m ${remainder}s`
  }
  const hours = Math.floor(minutes / 60)
  const minutesRemainder = minutes % 60
  return `${hours}h ${minutesRemainder}m`
}

const formatDateTime = (value) => {
  if (!value) {
    return '—'
  }
  return new Date(value).toLocaleString()
}

function ProgressPanel({ tasks, overallProgress, events = [], analytics }) {
  const eventSources = analytics?.events_by_source ?? {}
  const perTask = analytics?.per_task ?? []

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
      {analytics && (
        <div className="mt-6 border-t border-white/10 pt-5">
          <h3 className="text-xs font-semibold uppercase tracking-[0.4em] text-slate-300 mb-4">
            Operations Analytics
          </h3>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="rounded-xl border border-white/10 bg-midnight/60 px-4 py-3 text-xs uppercase tracking-[0.35em] text-slate-200 shadow-inner">
              <div className="text-[11px] text-slate-300">Tasks Complete</div>
              <div className="mt-2 text-lg font-semibold text-white">
                {analytics.tasks_completed}/{analytics.tasks_total}
              </div>
            </div>
            <div className="rounded-xl border border-white/10 bg-midnight/60 px-4 py-3 text-xs uppercase tracking-[0.35em] text-slate-200 shadow-inner">
              <div className="text-[11px] text-slate-300">Events Logged</div>
              <div className="mt-2 text-lg font-semibold text-white">{analytics.events_total}</div>
              <div className="mt-1 text-[10px] text-slate-400">
                {analytics.last_event_at ? `Latest • ${formatDateTime(analytics.last_event_at)}` : 'No events yet'}
              </div>
            </div>
            <div className="rounded-xl border border-white/10 bg-midnight/60 px-4 py-3 text-xs uppercase tracking-[0.35em] text-slate-200 shadow-inner">
              <div className="text-[11px] text-slate-300">In Progress</div>
              <div className="mt-2 text-lg font-semibold text-white">{analytics.tasks_in_progress}</div>
              <div className="mt-1 text-[10px] text-slate-400">Not Started • {analytics.tasks_not_started}</div>
            </div>
            <div className="rounded-xl border border-white/10 bg-midnight/60 px-4 py-3 text-xs uppercase tracking-[0.35em] text-slate-200 shadow-inner">
              <div className="text-[11px] text-slate-300">Avg Completion Time</div>
              <div className="mt-2 text-lg font-semibold text-white">
                {formatDuration(analytics.average_completion_seconds)}
              </div>
            </div>
          </div>
          <div className="mt-4 space-y-3">
            <div>
              <h4 className="text-[10px] font-semibold uppercase tracking-[0.4em] text-slate-400 mb-2">
                Events by Source
              </h4>
              <div className="flex flex-wrap gap-2 text-[11px] uppercase tracking-[0.3em] text-slate-200">
                {Object.keys(eventSources).length === 0 && <span className="text-slate-500">—</span>}
                {Object.entries(eventSources).map(([source, count]) => (
                  <span
                    key={source}
                    className="rounded-full border border-white/10 bg-white/5 px-3 py-1 shadow"
                  >
                    {source}: {count}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <h4 className="text-[10px] font-semibold uppercase tracking-[0.4em] text-slate-400 mb-2">
                Task Telemetry Summary
              </h4>
              <div className="space-y-3 max-h-48 overflow-y-auto pr-1">
                {perTask.length === 0 && (
                  <div className="rounded-xl border border-white/10 bg-midnight/60 px-4 py-3 text-[11px] uppercase tracking-[0.35em] text-slate-400">
                    No tasks tracked yet.
                  </div>
                )}
                {perTask.map((entry) => (
                  <div
                    key={entry.name}
                    className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-[11px] shadow-inner"
                  >
                    <div className="flex items-center justify-between uppercase tracking-[0.3em] text-slate-200">
                      <span>{entry.name}</span>
                      <span>{entry.progress}%</span>
                    </div>
                    <div className="mt-2 grid grid-cols-2 gap-2 text-[10px] uppercase tracking-[0.25em] text-slate-400">
                      <div>Events • {entry.events_count}</div>
                      <div>Completed • {entry.completed ? 'Yes' : 'No'}</div>
                      <div>Last • {formatDateTime(entry.last_event_at)}</div>
                      <div>Source • {entry.last_event_source ?? '—'}</div>
                    </div>
                    <div className="mt-2 text-[10px] uppercase tracking-[0.25em] text-slate-400">
                      Completion Time • {formatDuration(entry.seconds_to_completion)}
                    </div>
                    {entry.last_event_note && (
                      <p className="mt-2 text-[11px] leading-relaxed text-slate-200/80">
                        {entry.last_event_note}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProgressPanel
