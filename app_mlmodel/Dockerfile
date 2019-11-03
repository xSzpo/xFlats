# Use an official Python runtime as a parent image
# docker run -it python:3.7-alpine /bin/ash
# docker run -it python:3.7.2-slim bash
# docker exec -it <container-name/ID> bash
#FROM python:3.6-slim

FROM python:3.7-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN apt-get update \
    && apt-get install libgomp1
RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8080

# run
CMD ["python", "-u","/app/docker_app.py"]


