function ProgressPanel({ tasks, overallProgress }) {
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
    </div>
  )
}

export default ProgressPanel
