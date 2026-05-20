# taskiq/tasks.py

#region imports

from app.taskiq.broker import broker
from app.core.config import settings
from app.enums import Source
from app.services.lk_integration import LkIntegrationService

#endregion

_CRON_TZ = "Asia/Yekaterinburg"

@broker.task(
    schedule = [
        {"cron": "0 10 5 * *", "args": [settings.LK_FINANCE_LOGIN, settings.LK_FINANCE_PASSWORD, Source.LK_FINANCE], "cron_offset": _CRON_TZ},
        {"cron": "0 11 5 * *", "args": [settings.LK_ITSK_LOGIN, settings.LK_ITSK_PASSWORD, Source.LK_ITSK], "cron_offset": _CRON_TZ},
        {"cron": "0 12 5 * *", "args": [settings.LK_TECHNOLOGY_LOGIN, settings.LK_TECHNOLOGY_PASSWORD, Source.LK_TECHNOLOGY], "cron_offset": _CRON_TZ},
    ]
)
async def task_data_from_lk(login: str, password: str, source: Source) -> None:
    """
    Задача для сбора данных из ЛК Билайн и отправки их в целевой API
    """
    service = LkIntegrationService(api_url = settings.API_URL, api_token = settings.API_TOKEN)
    await service.process_and_send(login = login, password = password, source = source)
