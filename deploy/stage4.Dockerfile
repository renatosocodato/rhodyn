FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE NOTICE MANIFEST.in ./
COPY src ./src

RUN python -m pip install --no-cache-dir '.[backend]'

ENV RHODYN_JOB_STORE_DIR=/var/lib/rhodyn/jobs
RUN mkdir -p /var/lib/rhodyn/jobs

EXPOSE 8000

CMD ["uvicorn", "rhodyn.backend:app", "--host", "0.0.0.0", "--port", "8000"]
