#!/bin/bash

image_tag=$1
image_name="auerbwaretelegrambot"

docker build -t ghcr.io/hir0ki/$image_name:$image_tag .