# Install OS environment.
FROM python:3.11-slim
LABEL name="tiptabs"
LABEL mainainer="Gary McDonald"
LABEL description="Python web application that simplifies conversions between established currencies."

# Install system dependencies
RUN apt-get update && \
  apt-get install -y git && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel.
RUN pip install --upgrade pip setuptools wheel

# Set working directory
WORKDIR /app

# Copy local files into container.
COPY . .

# Install application in editable mode
RUN pip3 install -e .

# Expose port for Flask.
EXPOSE 5000

# Run main.py.
CMD ["tiptabs"]