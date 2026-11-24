FROM apache/airflow:2.10.1-python3.12

# Set user to root to install system dependencies if needed (e.g., libpq-dev)
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         build-essential \
         libpq-dev \
         curl \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy and install Python dependencies
COPY airflow/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Set PYTHONPATH to include the /opt/airflow directory so it can find the mounted etl module
ENV PYTHONPATH="${PYTHONPATH}:/opt/airflow"
