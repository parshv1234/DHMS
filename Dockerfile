FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Use the correct repository and install OpenJDK 17
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget gnupg software-properties-common && \
    echo "deb [arch=arm64] http://deb.debian.org/debian bookworm main" > /etc/apt/sources.list.d/bookworm.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends openjdk-17-jdk-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/bookworm.list


# Set environment variables for Java
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 5000

# Start the Flask application
CMD ["python", "app.py"]
