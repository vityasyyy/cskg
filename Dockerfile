# Start from a slim, official Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt requirements.txt

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your new, organized code directories into the container
COPY ./server /app/server
COPY ./pipeline /app/pipeline

# Note: We still don't need a CMD or ENTRYPOINT.
# The compose file will provide the commands.
