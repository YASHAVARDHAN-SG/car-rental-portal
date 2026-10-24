#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.prod.yml"
NGINX_CONFIG="$SCRIPT_DIR/nginx.conf"

required_variables=(AWS_REGION ECR_REGISTRY ECR_REPOSITORY IMAGE_TAG PUBLIC_HOST)
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
sudo mkdir -p "$SCRIPT_DIR/data" "$SCRIPT_DIR/media"
sudo chmod 0750 "$SCRIPT_DIR/data"
sudo chown -R 10001:10001 "$SCRIPT_DIR/data"
sudo chmod 0755 "$SCRIPT_DIR/media"
sudo chown -R 10001:10001 "$SCRIPT_DIR/media"
docker compose --project-directory "$SCRIPT_DIR" -f "$COMPOSE_FILE" up -d --remove-orphans

container_id="$(docker compose --project-directory "$SCRIPT_DIR" -f "$COMPOSE_FILE" ps -q web)"
if [[ -z "$container_id" ]]; then
  echo "Compose did not create the web container." >&2
  docker compose --project-directory "$SCRIPT_DIR" -f "$COMPOSE_FILE" ps
  docker compose --project-directory "$SCRIPT_DIR" -f "$COMPOSE_FILE" logs --tail=100 web
  exit 1
fi

healthy=false
for attempt in $(seq 1 120); do
  container_state="$(docker inspect --format '{{.State.Status}}' "$container_id")"
  health_status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}missing{{end}}' "$container_id")"

  if [[ "$container_state" != "running" ]]; then
    echo "Web container entered state '$container_state' before becoming healthy." >&2
    docker compose --project-directory "$SCRIPT_DIR" -f "$COMPOSE_FILE" ps
    docker compose --project-directory "$SCRIPT_DIR" -f "$COMPOSE_FILE" logs --tail=100 web
    exit 1
  fi

  if [[ "$health_status" == "healthy" ]]; then
    healthy=true
    break
  fi

  if [[ "$health_status" == "unhealthy" || "$health_status" == "missing" ]]; then
    echo "Web container health check status is '$health_status'." >&2
    docker compose --project-directory "$SCRIPT_DIR" -f "$COMPOSE_FILE" ps
    docker compose --project-directory "$SCRIPT_DIR" -f "$COMPOSE_FILE" logs --tail=100 web
    exit 1
  fi

  sleep 2
done

if [[ "$healthy" != "true" ]]; then
  echo "Timed out waiting for the web container health check." >&2
  docker compose --project-directory "$SCRIPT_DIR" -f "$COMPOSE_FILE" ps
  docker compose --project-directory "$SCRIPT_DIR" -f "$COMPOSE_FILE" logs --tail=100 web
  exit 1
fi

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nginx curl
sed "s|__MEDIA_ROOT__|$SCRIPT_DIR/media|g" "$NGINX_CONFIG" \
  | sudo tee /etc/nginx/sites-available/car-rental >/dev/null
sudo chmod 644 /etc/nginx/sites-available/car-rental
sudo ln -sfn /etc/nginx/sites-available/car-rental /etc/nginx/sites-enabled/car-rental
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx

if ! curl --fail --silent --show-error http://127.0.0.1/ >/dev/null; then
  echo "The web container is healthy, but the Nginx proxy check failed." >&2
  sudo journalctl -u nginx --no-pager -n 50
  docker compose --project-directory "$SCRIPT_DIR" -f "$COMPOSE_FILE" ps
  docker compose --project-directory "$SCRIPT_DIR" -f "$COMPOSE_FILE" logs --tail=100 web
  exit 1
fi

echo "Deployment healthy: $APP_IMAGE"
