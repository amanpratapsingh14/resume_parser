FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc build-essential

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy all code
COPY . .

# Expose ports for FastAPI and Streamlit
EXPOSE 8080 8501

# Entrypoint: run FastAPI backend directly
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]