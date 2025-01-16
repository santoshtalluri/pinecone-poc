FROM python:3.11-slim

WORKDIR /app

# Install necessary build tools
RUN apt-get update && apt-get install -y build-essential python3-dev

# Upgrade pip
RUN pip install --upgrade pip

COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Install dependencies
RUN pip install -r requirements.txt

CMD ["python", "main.py"]