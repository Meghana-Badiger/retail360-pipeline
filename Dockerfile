# Start from the same official Airflow image we were using
FROM apache/airflow:2.8.1

# Switch to root — installing system packages (Java) needs admin rights
USER root

# Install Java 17 (PySpark runs on the JVM), then delete apt cache to keep image small
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Tell PySpark where Java is installed
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Switch back to the normal airflow user — Airflow should not run as root
USER airflow

# Install Python packages; pinning apache-airflow stops pip from upgrading/breaking Airflow
RUN pip install --no-cache-dir \
    "apache-airflow==2.8.1" \
    pyspark==3.5.1 \
    faker==24.4.0