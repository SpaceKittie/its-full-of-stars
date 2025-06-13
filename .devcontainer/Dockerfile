FROM mcr.microsoft.com/devcontainers/python:0-3.11

WORKDIR /workspaces

COPY requirements-dev.txt .

RUN pip install --no-cache-dir -r requirements-dev.txt

RUN curl -sSL https://install.astronomer.io | bash