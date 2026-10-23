#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.prod.yml"
NGINX_CONFIG="$SCRIPT_DIR/nginx.conf"

required_variables=(AWS_REGION ECR_REGISTRY ECR_REPOSITORY IMAGE_TAG)
for variable in "${required_variables[@]}"; do
  if [[ -z "${!variable:-}" ]]; then
    echo "Required environment variable $variable is not set." >&2
    exit 1
  fi
done

if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
  echo "Missing $SCRIPT_DIR/.env; create the application environment file before deploying." >&2
  exit 1
fi

if [[ ! -f "$COMPOSE_FILE" || ! -f "$NGINX_CONFIG" ]]; then
  echo "Compose file or Nginx configuration is missing from $SCRIPT_DIR." >&2
  exit 1
fi

if ! command -v aws >/dev/null 2>&1; then
  echo "AWS CLI is required on EC2 to authenticate to ECR using the instance profile." >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose plugin is required on EC2." >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "The current EC2 user cannot access the Docker daemon." >&2
  exit 1
fi

if ! sudo -n true 2>/dev/null; then
  echo "The EC2 user needs passwordless sudo to configure host Nginx." >&2
  exit 1
fi

export APP_IMAGE="$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG"

aws ecr get-login-password --region "$AWS_REGION" |
  docker login --username AWS --password-stdin "$ECR_REGISTRY"

docker compose --project-directory "$SCRIPT_DIR" -f "$COMPOSE_FILE" config --quiet
docker compose --project-directory "$SCRIPT_DIR" -f "$COMPOSE_FILE" pull web
docker compose --project-directory "$SCRIPT_DIR" -f "$COMPOSE_FILE" up -d --remove-orphans

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nginx curl
sudo install -m 644 "$NGINX_CONFIG" /etc/nginx/sites-available/car-rental
sudo ln -sfn /etc/nginx/sites-available/car-rental /etc/nginx/sites-enabled/car-rental
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx

for attempt in $(seq 1 60); do
  if curl --fail --silent --show-error http://127.0.0.1/ >/dev/null; then
    echo "Deployment healthy: $APP_IMAGE"
    exit 0
  fi
  sleep 2
done

docker compose --project-directory "$SCRIPT_DIR" -f "$COMPOSE_FILE" logs --tail=100 web
exit 1
