FROM python:3.13-alpine

# no pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# no buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --no-cache \
    build-base \
    && rm -rf /var/cache/apk/*

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

USER appuser


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]