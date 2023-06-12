# Base image
FROM python:3.11-bullseye AS base

ARG DEV=0

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install requirements based on DEV arg
RUN if [ "$DEV" = "1" ] ; then \
    pip install --no-cache-dir -r  requirements.txt -r requirements-dev.txt ; \
    else \
    pip install --no-cache-dir -r requirements.txt ; \
    fi

# Production image
FROM python:3.11-slim AS output

ARG DEV=0

# Create and activate virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Install app dependencies from the initial venv
COPY --from=base /opt/venv /opt/venv

WORKDIR /app

# Copy app code
COPY . .

# Build app
RUN if [ "$DEV" != "1" ] ; then python -m compileall . ; fi

# Expose port
EXPOSE 8080

CMD if [ "$ENV" = "dev" ] ; then \
    uvicorn app.main:app --host 0.0.0.0 --reload ; \
    else \
    uvicorn app.main:app --host 0.0.0.0 ; \
    fi
