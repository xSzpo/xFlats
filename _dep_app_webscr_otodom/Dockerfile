# Use an official Python runtime as a parent image
# docker run -it python:3.7-alpine /bin/ash
# docker run -it python:3.7.2-slim bash
#FROM python:3.6-slim

FROM python:3.7-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# set scraper start delay
ENV SCRAPER_START_DELAY_SEC 60

# run
CMD ["python", "-u","/app/docker_app.py"]


