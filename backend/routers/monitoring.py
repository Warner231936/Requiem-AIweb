from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.analytics import compute_progress_analytics


router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/metrics", response_class=PlainTextResponse)
def metrics(db: Session = Depends(get_db)) -> str:
    """Expose Prometheus-style metrics for external monitoring systems."""

    analytics = compute_progress_analytics(db)

    lines = [
        "# HELP requiem_tasks_total Total number of tasks tracked by Requiem.",
        "# TYPE requiem_tasks_total gauge",
        f"requiem_tasks_total {analytics.tasks_total}",
        "# HELP requiem_tasks_completed Number of tasks completed (progress == 100).",
        "# TYPE requiem_tasks_completed gauge",
        f"requiem_tasks_completed {analytics.tasks_completed}",
        "# HELP requiem_tasks_in_progress Tasks with a non-zero, non-complete progress value.",
        "# TYPE requiem_tasks_in_progress gauge",
        f"requiem_tasks_in_progress {analytics.tasks_in_progress}",
        "# HELP requiem_tasks_not_started Tasks that have not started yet.",
        "# TYPE requiem_tasks_not_started gauge",
        f"requiem_tasks_not_started {analytics.tasks_not_started}",
        "# HELP requiem_events_total Total telemetry events recorded.",
        "# TYPE requiem_events_total counter",
        f"requiem_events_total {analytics.events_total}",
        "# HELP requiem_overall_progress Average progress percentage across all tasks.",
        "# TYPE requiem_overall_progress gauge",
        f"requiem_overall_progress {analytics.overall_progress}",
    ]

    for source, count in sorted(analytics.events_by_source.items()):
        lines.append(
            f'requiem_events_by_source{{source="{source}"}} {count}'
        )

    if analytics.average_completion_seconds is not None:
        lines.extend(
            [
                "# HELP requiem_average_completion_seconds Average seconds to completion for completed tasks.",
                "# TYPE requiem_average_completion_seconds gauge",
                f"requiem_average_completion_seconds {analytics.average_completion_seconds}",
            ]
        )

    for entry in analytics.per_task:
        labels = f'task="{entry.name}"'
        lines.append(
            f"requiem_task_progress{{{labels}}} {entry.progress}"
        )
        lines.append(
            f"requiem_task_events{{{labels}}} {entry.events_count}"
        )
        if entry.seconds_to_completion is not None:
            lines.append(
                f"requiem_task_completion_seconds{{{labels}}} {entry.seconds_to_completion}"
            )

    return "\n".join(lines) + "\n"

