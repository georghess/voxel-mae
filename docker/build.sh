#!/bin/sh

export DOCKER_NAME=mmdetection3d
export DOCKER_ROOT=..

# Build docker image
docker build -f Dockerfile -t $DOCKER_NAME $DOCKER_ROOT

# Convert to singularity
# singularity build mmdetection3d.sif docker-daemon://mmdetection3d:latest
