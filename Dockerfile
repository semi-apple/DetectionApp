# syntax=docker/dockerfile:1

# set base image to the 22.04 release of Ubuntu
FROM ubuntu:22.04

# install app dependencies
RUN apt-get update && apt-get install -y python3 python3-pip

# create work dir
WORKDIR /app

# copy all code to work dir
COPY . /app

# Install python packages with pip
RUN RUN echo "(*) Installing python packages with pip..." \
    pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python3", "main.py"]
