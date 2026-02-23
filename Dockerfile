FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy test code (credentials in env/ are never baked in)
COPY tests/ tests/

VOLUME ["/app/allure-results"]

ENV ENV=prod

ENTRYPOINT ["python", "-m", "pytest"]
CMD ["-v", "--alluredir=/app/allure-results"]
