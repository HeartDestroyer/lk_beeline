FROM python:3.12-slim

WORKDIR /app

# Устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg2 \
    curl \
    unzip \
    gpg \
    && rm -rf /var/lib/apt/lists/*

# Создаем директорию для доверенных ключей и скачиваем ключ Google Chrome современным методом
RUN mkdir -p /etc/apt/keyrings \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Устанавливаем Google Chrome и очищаем кэш apt
RUN apt-get update && apt-get install -y --no-install-recommends google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем переменную для корректной работы headless Chrome
ENV DISPLAY=:99

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY app/ app/