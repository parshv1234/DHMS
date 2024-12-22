# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install Java (OpenJDK)
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk && \
    apt-get clean

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application files
COPY . .

# Set the environment variable for Java
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Expose the port your app will run on
EXPOSE 5000

# Run your app
CMD ["python", "__init__.py"]
