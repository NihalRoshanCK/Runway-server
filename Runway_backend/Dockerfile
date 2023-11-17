# Use the official Python 3 image as the base image
FROM python:3.10

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Install system dependencies including libgdal-dev and libffi-dev
RUN apt-get update && \
    apt-get install -y libgdal-dev libffi-dev netcat-openbsd

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Upgrade pip and setuptools
RUN pip install --upgrade pip setuptools 

# Install Python dependencies using pip
RUN pip install -r requirements.txt 


COPY ./entrypoint.sh .
RUN chmod +x ./entrypoint.sh

# Copy the rest of the application code into the container
COPY . .

# Start the Django development server
# CMD ["python3", "manage.py", "runserver" ,"0.0.0.0:8000" ]

ENTRYPOINT ["./entrypoint.sh"]

# Start Daphne for ASGI
#CMD ["daphne", "-b", "0.0.0.0", "-p", "8001", "Runway_backend.asgi:application"]