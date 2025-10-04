#!/usr/bin/env bash

memory=$1
cpu=$2
size=$3
archive_path=$4

docker build -f container/Dockerfile -t unarchive-test container/

ext="${archive_path##*.}"

docker run --rm \
  --memory="${memory}m" \
  --cpus="$cpu" \
  --tmpfs "/bomb:size=${size}m" \
  -v "$archive_path":/bomb/bomb.$ext \
  -v "$(pwd)/report_output":/report_output \
  unarchive-test
