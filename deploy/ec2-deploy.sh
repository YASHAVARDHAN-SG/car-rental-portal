#!/usr/bin/env bash
set -Eeuo pipefail

region="${1:?AWS region is required}"
registry="${2:?ECR registry is required}"
image="${3:?ECR image URI is required}"
nginx_config_base64="${4:?Base64-encoded Nginx config is required}"

if [[ ! -f /opt/car-rental/.env ]]; then
  echo "Missing /opt/car-rental/.env; create the Django environment file before deploying."
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed on this EC2 instance."
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y awscli nginx curl

aws ecr get-login-password --region "$region" |
  docker login --username AWS --password-stdin "$registry"
docker pull "$image"

install -d -m 755 /opt/car-rental/data
chown 10001:10001 /opt/car-rental/data

install -d -m 755 /etc/nginx/sites-available
printf '%s' "$nginx_config_base64" | base64 --decode > /etc/nginx/sites-available/car-rental
ln -sfn /etc/nginx/sites-available/car-rental /etc/nginx/sites-enabled/car-rental
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl enable --now nginx

if docker inspect car-rental >/dev/null 2>&1; then
  docker rm -f car-rental
fi

docker run --detach --name car-rental --restart unless-stopped \
  --env-file /opt/car-rental/.env \
  --publish 127.0.0.1:8000:8000 \
  --mount type=bind,source=/opt/car-rental/data,target=/app/data \
  "$image"

for attempt in $(seq 1 60); do
  status="$(docker inspect --format '{{.State.Health.Status}}' car-rental 2>/dev/null || true)"
  if [[ "$status" == healthy ]]; then
    nginx -t
    systemctl reload nginx
    curl --fail --silent --show-error http://127.0.0.1/
    exit 0
  fi
  sleep 2
done

docker logs car-rental
exit 1
