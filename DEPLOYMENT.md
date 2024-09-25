# Secure File Sharing System Deployment

This document explains how to deploy the Secure File Sharing System using **Docker** and **SQLite**.

## Prerequisites

- Install [Docker](https://docs.docker.com/get-docker/)
- Install [Docker Compose](https://docs.docker.com/compose/install/)

## 1. Dockerize the Application

### Dockerfile

Create a `Dockerfile` in the root directory of your project with the following content:

```Dockerfile
# Use the official Python image as the base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose the port Django will run on
EXPOSE 8000

# Run database migrations and start the Django development server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
```

## 2. Docker Compose Configuration

Create a docker-compose.yml file in the root directory with the following content:

```docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - redis

  redis:
    image: "redis:alpine"
```
## Environment Variables
```
  environment:
      - DJANGO_SECRET_KEY=your_secret_key_here
      - EMAIL_HOST_USER=your_email@gmail.com
      - EMAIL_HOST_PASSWORD=your_email_password_here
```

## 3. Install Requirements

Make sure your requirements.txt contains the necessary dependencies for the project. Here’s an example:

```
Django>=3.2,<4.0
djangorestframework
django-cors-headers
PyJWT
redis
```

## 4.  Building and Running the Application

Once the Dockerfile and docker-compose.yml are set up, follow these steps to build and run the application:

## Build the Docker image:
docker-compose build

## Run the container:
docker-compose up

### The app will be available at http://localhost:8000.

## 5. Production Deployment
For deploying to production, you can use cloud platforms such as:

Heroku
DigitalOcean
AWS EC2
Railway.app
Render.com

Configure your environment variables and ensure you back up the SQLite database if necessary.

