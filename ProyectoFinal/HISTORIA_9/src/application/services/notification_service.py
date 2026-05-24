import asyncio

from src.core.console import console
from src.domain.events.job_completed import JobCompletedEvent
from src.infrastructure.websocket.manager import ws_manager


class NotificationService:
    @staticmethod
    def notify_job_completed(event: JobCompletedEvent) -> None:
        asyncio.run(_dispatch(event))


async def _dispatch(event: JobCompletedEvent) -> None:
    payload = {
        "type": "job_completed",
        "job_id": event.job_id,
        "user_id": event.user_id,
        "result": event.result_summary,
        "event_id": event.event_id,
        "occurred_at": event.occurred_at.isoformat(),
    }
    await ws_manager.notify(event.user_id, payload)
    console.log(
        f"[success]Notificación enviada[/] a user [info]{event.user_id}[/] "
        f"por job [amount]{event.job_id}[/]"
    )
