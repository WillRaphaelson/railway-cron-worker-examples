FROM python:3.13-slim
WORKDIR /app
COPY check_once.py worker.py ./
ENV PYTHONUNBUFFERED=1
CMD ["python", "worker.py"]
