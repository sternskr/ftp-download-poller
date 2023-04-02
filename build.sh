#!/bin/bash

# Build the Docker image with the specified tag
docker build -t ftp-download-poller .

# Push the Docker image to the registry
docker tag ftp-download-poller sternskr/ftp-download-poller:latest
docker push sternskr/ftp-download-poller:latest

# Remove the local Docker image
docker rmi ftp-download-poller