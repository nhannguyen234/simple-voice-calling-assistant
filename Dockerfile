FROM python:3.11-slim-bullseye

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
        libgl1-mesa-glx \
        libglib2.0-0 \
        ffmpeg \
        portaudio19-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . /code/
ENV PYTHONPATH="${PYTHONPATH}:/code/"

CMD ["uv", "run", "python", "main.py"]
