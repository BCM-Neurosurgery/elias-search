#!/bin/bash
set -e

export DOCKER_BUILDKIT=1  # ⬅ Enable BuildKit

# add ssh agent
eval `ssh-agent -s`

if [ -f ~/.ssh/id_ed25519 ]; then
  ssh-add ~/.ssh/id_ed25519
elif [ -f ~/.ssh/id_rsa ]; then
  ssh-add ~/.ssh/id_rsa
else
  echo "Missing ssh key"
  exit 1
fi

# source env
source ./.env

docker compose build --ssh default
docker compose up -d