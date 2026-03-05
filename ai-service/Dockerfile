FROM python:3.12-slim

# ដំឡើង dependencies សម្រាប់ PostgreSQL និង GCC
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ចម្លង requirements និងដំឡើង (ប្រើ numpy<2.0.0 ដើម្បីកុំឱ្យ Error)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ចម្លងកូដទាំងអស់ចូល
COPY . .

# សំខាន់៖ Hugging Face ប្រើ Port 7860 ជា Default
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
