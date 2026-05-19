# services/lk_integration.py

#region imports

import io
import csv
import asyncio
import logging
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

from app.utils.parse import parse_from_lk
from app.enums import Source

logger = logging.getLogger(__name__)

#endregion

class LkIntegrationService:
    """
    Сервис для интеграции с ЛК Билайн и отправки данных в целевой API
    """

    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url
        self.api_token = api_token

    async def process_and_send(self, login: str, password: str, source: Source) -> None:
        """
        Метод для сбора данных из ЛК Билайн и отправки их в целевой API
        """
        logger.info(f"ЛК Билайн | Cбор данных для источника: {source.value}")
        
        lines = await asyncio.to_thread(parse_from_lk, login, password)
        
        file_buffer = await asyncio.to_thread(self._build_csv_in_memory, lines, source)
        
        await self._send_file_to_api(file_buffer)

        logger.info(f"ЛК Билайн | Файл для {source.value} успешно отправлен в целевой API")

    def _build_csv_in_memory(self, lines: list[str], source: Source) -> io.BytesIO:
        """
        Метод для формирования CSV в оперативной памяти
        """
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=";")
        
        # Защита - если колонка 15 пустая - пропускаем
        BASE_STATION_INDEX = 15
        
        reader = csv.reader(lines, delimiter=";")
        try:
            headers = next(reader)
            writer.writerow(headers)
        except StopIteration:
            return io.BytesIO(b"")

        for row in reader:
            if len(row) > BASE_STATION_INDEX and not row[BASE_STATION_INDEX]:
                continue
            writer.writerow(row)
        
        byte_buffer = io.BytesIO(buffer.getvalue().encode('utf-8'))
        byte_buffer.name = f"lk_beeline_export_{source.value.lower()}.csv"
        return byte_buffer

    @retry(stop = stop_after_attempt(3), wait = wait_exponential(multiplier = 2, min = 2, max = 10))
    async def _send_file_to_api(self, file_buffer: io.BytesIO) -> None:
        """
        Метод для отправки файла в целевой API
        """
        headers = {"X-API-Key": self.api_token}
        
        data = aiohttp.FormData()
        data.add_field('file', file_buffer, filename = file_buffer.name, content_type = 'text/csv')

        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, data = data, headers = headers) as response:
                if response.status == 422:
                    error_text = await response.text()
                    logger.error(f"ЛК Билайн | Ошибка валидации 422 | Текст ошибки: {error_text}")
                elif response.status not in [200, 201]:
                    error_text = await response.text()
                    logger.error(f"ЛК Билайн | Ошибка API | Статус: {response.status} | Текст ошибки: {error_text}")
                response.raise_for_status()
