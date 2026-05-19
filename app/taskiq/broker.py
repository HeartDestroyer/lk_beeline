# taskiq/broker.py

#region imports

from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListQueueBroker

from app.core.config import settings

#endregion

broker = ListQueueBroker(settings.BROKER_URL)

scheduler = TaskiqScheduler(broker = broker, sources = [LabelScheduleSource(broker)])
