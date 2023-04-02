#!/bin/bash

# Build the Docker image with the specified tag
docker build -t my-poll-ftp-image .

# Log in to the Docker registry
docker login --username=yourusername --password=yourpassword

# Push the Docker image to the registry
docker tag my-poll-ftp-image yourregistry/my-poll-ftp-image:latest
docker push yourregistry/my-poll-ftp-image:latest

# Log out of the Docker registry
docker logout

# Remove the local Docker image
docker rmi my-poll-ftp-image