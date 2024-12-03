# Dockerfile for gym_reader

# Use an official Python runtime as a parent image
FROM python:3.11

# Set work directory
WORKDIR /app/gym_reader

# Install Poetry
RUN pip install poetry

# Install supervisor
RUN apt-get update && apt-get install -y supervisor

# Copy pyproject.toml and poetry.lock if present
COPY pyproject.toml poetry.lock* /app/gym_reader/
# Copy the supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi  

# Add Poetry's bin directory to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy the rest of the application code
COPY . /app/gym_reader/

# Expose the port the app runs on
EXPOSE 8000
WORKDIR /app/

# Command to run supervisord
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
