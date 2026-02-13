FROM python:3.11-slim

WORKDIR /project

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies

# Copy requirements.txt
COPY webapp/requirements.txt /project/requirements.txt

# Install requirements
RUN pip install --no-cache-dir -r /project/requirements.txt

# Install Plotly explicitly
RUN pip install --no-cache-dir plotly

# Copy project code
COPY webapp /project/webapp
COPY scrapy /project/scrapy

# Expose Streamlit port
EXPOSE 8501

# Start import + Streamlit webapp
CMD ["bash", "-lc", "python /project/webapp/app/import_characters.py && streamlit run /project/webapp/app/main.py"]
