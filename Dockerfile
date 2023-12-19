# Use Ubuntu as the base image
FROM ubuntu:latest

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install necessary packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install required Python packages
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the port your app runs on
EXPOSE 8001

# Command to run your application
CMD ["python3", "app.py"]


# # First stage: Use Ubuntu for building Python environment
# FROM ubuntu:latest AS builder

# # Set environment variables
# ENV DEBIAN_FRONTEND=noninteractive

# # Install system dependencies and Python
# RUN apt-get update && apt-get install -y \
#     python3 \
#     python3-pip \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# RUN mkdir -p /src  && mkdir -p /opt

# COPY . /src
# # Set the working directory inside the container
# WORKDIR /src

# # Copy requirements and install Python dependencies
# COPY requirements.txt requirements.txt
# RUN pip3 install --no-cache-dir -r requirements.txt

# # Second stage: Use Alpine for a smaller final image
# FROM python:3.9-alpine

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# # Copy necessary files from the builder stage
# COPY --from=builder /usr /usr
# COPY --from=builder /src /src

# # Set the working directory inside the container
# WORKDIR /src

# # Expose the port your app runs on
# EXPOSE 5000

# # Command to run your application
# CMD ["python", "app.py"]


