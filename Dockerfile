FROM python:3.12
WORKDIR /app
COPY citadel /app/citadel/
COPY pyproject.toml poetry.lock README.md /app/
RUN pip install poetry
RUN poetry install
CMD ["poetry", "run", "python3", "citadel/main.py"]
