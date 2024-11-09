FROM python:3.13-slim

WORKDIR /app

# Install dependencies directly
RUN pip install --no-cache-dir anthropic python-dotenv

# Create a directory for data
RUN mkdir /app/data

# Copy the application code and data
COPY agents.py .
COPY prompts.py .
COPY polite-persuasive-responses.csv /app/data/

# Set volume for data
VOLUME ["/app/data"]

CMD ["python", "agents.py"]
