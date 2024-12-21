FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app

COPY . /app

CMD["uvicorn server:app --host 0.0.0.0 --port 8000"]