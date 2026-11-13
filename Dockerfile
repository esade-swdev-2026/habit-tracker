FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY README.md LICENSE ./
COPY src ./src
RUN uv sync --locked --no-dev

RUN useradd --create-home app && mkdir /app/data && chown app:app /app/data
USER app

ENV PATH="/app/.venv/bin:$PATH"
ENV HABIT_TRACKER_FILE=/app/data/habits.json
ENTRYPOINT ["habit-tracker"]
CMD ["--help"]
