# Use an official Python runtime as a parent image
# docker run -it python:3.7-alpine /bin/bash
# docker run -it python:3.7.2-slim bash
#FROM python:3.6-slim

FROM python:3.7-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# run
ENTRYPOINT ["python", "-u","/app/app.py"]
