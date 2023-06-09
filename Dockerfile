# Base image
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install production requirements
RUN pip install --no-cache-dir -r requirements.txt

# Development image
FROM base AS dev

# Copy dev requirements file
COPY requirements-dev.txt .

# Install dev requirements if DEV_BUILD is set
ARG DEV_BUILD
RUN if [ "$DEV_BUILD" = "true" ] ; then pip install --no-cache-dir -r requirements-dev.txt ; fi

# Build image
FROM base AS build

# Copy app code
COPY . .

# Set environment variable
ENV APP_MODULE=main:app

# Build app
RUN python -m compileall .

# Production image
FROM base AS prod

# Copy compiled app code
COPY --from=build /app .

# Expose port
EXPOSE 8000

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
