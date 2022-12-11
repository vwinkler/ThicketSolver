#!/bin/sh

if [ $# -ne 2 ]
then
    echo "Usage: $0 WIDTH HEIGHT"
    exit 1
fi

echo "Building docker container.."
BUILDOUTPUT=$(docker build .)
if [[ $? -ne 0 ]]
then
    echo "Could not build docker container."
    exit 1
fi
HASH=$(echo "$BUILDOUTPUT" | tail -1)
echo "Finished building docker container as $HASH"
echo "Running inside docker container $HASH.."
docker run $HASH $1 $2
echo "Docker container terminated"
