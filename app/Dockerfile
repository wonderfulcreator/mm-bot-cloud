FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/data /app/data/logs
CMD ["python", "bot.py"]
