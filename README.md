# 🚗 DriveEase - Car Rental Management System

A full-stack **Car Rental Management System** built using **Django**, featuring user authentication, car booking, admin management, and dynamic price calculation. This project is suitable for academic submissions, portfolio showcasing, and real-world learning.

---

## 📌 Features

### 👤 Authentication
- User Registration
- User Login & Logout
- Session-based authentication
- Public car browsing, with booking restricted to logged-in users
- Login and registration forms validate credentials and show errors

### 🚘 Car Management
- Add, update, and delete cars via Admin Panel
- Set car availability
- Set the rental price, vehicle photo, description, fuel type, transmission, and seating capacity

### 📅 Booking System
- Book cars by selecting travel dates, pick-up location, and drop-off location
- Automatic total price calculation
- User-specific booking history with detailed trip and vehicle specifications
- Cancel bookings from the reservation details page; cancellations remain in history
- Secure backend validation

### 🛠 Admin Panel
- Manage users
- Manage cars
- View all bookings

---

## 🧰 Tech Stack

| Layer        | Technology |
|--------------|------------|
| Backend      | Django (Python) |
| Frontend     | HTML, CSS, JavaScript |
| Database     | SQLite |
| Auth         | Django Auth |
| ORM          | Django ORM |

---

## Continuous integration

CircleCI builds the Docker image, runs the Django unit-test job, and only then pushes the saved image to ECR. The deploy job runs after a successful push on `main`. The build image is passed between jobs using a CircleCI workspace so the tested commit's image is the one published. The deployment job copies the Compose file and deploy script to EC2 over SSH.

## Deploy to EC2 with Docker and ECR

The repository `Dockerfile` builds the Django runtime image. The `build-image` and `unit-tests` jobs run before `push-image`; the latter assumes the AWS role through OIDC and publishes the image to ECR. Deployment is restricted to the `main` branch.

### One-time AWS and EC2 setup

1. Create an ECR repository in the same AWS region as the EC2 instance. Set `ECR_REPOSITORY` to its repository name (not the full registry URI).
2. Configure the IAM role to trust CircleCI's OIDC identity provider for this CircleCI organization and project. Limit the trust policy to this project and grant the role only the ECR permissions needed to authenticate and push to the application repository. The deploy job exchanges CircleCI's OIDC token for temporary role credentials; it does not use IAM user access keys. If this role currently trusts GitHub Actions, add/configure CircleCI's OIDC provider and trust policy as well—GitHub's OIDC token cannot be used by CircleCI.
3. Attach an EC2 instance profile that grants ECR pull access (for example, `AmazonEC2ContainerRegistryReadOnly`). Docker, the Docker Compose plugin, AWS CLI, and passwordless `sudo` for Nginx setup are required on the instance. The instance needs outbound access to ECR and package repositories. Configure its security group to allow HTTP on port 80 and SSH from trusted CircleCI job egress addresses. Do not expose port 8000 publicly.
4. Create the Compose working directory and environment file in the Ubuntu user's home directory on EC2. The deployment copies `docker-compose.prod.yml`, `deploy.sh`, and `nginx.conf` to `~/car-rental` on every deploy; create `.env` once and keep it out of source control:

   ```bash
   mkdir -p ~/car-rental/data
   tee ~/car-rental/.env >/dev/null <<'EOF'
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=replace-with-a-long-random-secret
   DJANGO_ALLOWED_HOSTS=your-domain.example
   EOF
   chmod 600 ~/car-rental/.env
   ```

   Replace the example secret and domain before deployment. Keep this file on the instance; do not commit it. `DJANGO_ALLOWED_HOSTS` is a comma-separated list of custom domains; the deploy job automatically adds the EC2 host from `EC2_HOST` to the container's allowed hosts. Compose sets `DJANGO_DB_PATH=/app/data/db.sqlite3`; SQLite data persists in `~/car-rental/data` across container replacements. Before starting Compose, `deploy/deploy.sh` creates that host data directory and assigns it to the container's non-root UID/GID `10001`, which Django needs to write the SQLite database. The script sets `APP_IMAGE` to the ECR image URI, authenticates to ECR using the EC2 instance profile, runs Compose, and configures host Nginx to proxy port 80 to the app on localhost port 8000. Default Compose values allow `ps`, `logs`, and `exec` to work interactively without deployment variables; use the deploy script to update the service.

To create a Django admin account over SSH, run this from `~/car-rental`:

```bash
WEB_CONTAINER="$(docker ps -q --filter label=com.docker.compose.service=web | head -n 1)"
test -n "$WEB_CONTAINER" || { echo "The web container is not running."; exit 1; }
docker exec -it "$WEB_CONTAINER" python manage.py createsuperuser
```

This uses the running web container directly, so the admin command does not depend on Compose interpolation variables.
Manage the rental inventory at `http://<EC2_PUBLIC_IP>/admin/` after logging in with that admin account. Cars marked unavailable are not shown on the public homepage.
Add cars in the admin panel to populate the public car cards. Set each car's brand, name, daily price, availability, and photo. Prices on the site are displayed in USD. Visitors can browse without signing in; selecting **Book Now** prompts guests to log in or create an account, then returns them to that reservation.
5. Configure the CircleCI SSH key whose fingerprint is used by the `deploy` job, and add these project environment variables. Do not put secret values in the repository:

   | Variable | Value |
   | --- | --- |
   | `ECR_REPOSITORY` | Existing ECR repository name |
   | `EC2_HOST` | EC2 public DNS name or IP |
   | `EC2_USER` | SSH user, commonly `ubuntu` |

The `push-image` job assumes through CircleCI OIDC. The role trust policy should restrict access to this CircleCI project and the `main` branch, and its permissions should allow pushing to the ECR repository. The EC2 instance profile is separate and grants the instance pull access. The deploy job uses the configured CircleCI SSH key to connect to the host.

Set `AWS_REGION` to the ECR region and `ECR_REGISTRY` to the full ECR registry URI in CircleCI. The image is pushed to both the commit SHA tag and `latest`.

The EC2 application is currently published over HTTP through Nginx on port 80. Configure TLS (for example, with an HTTPS load balancer or a TLS-enabled Nginx configuration) before using it to handle real user credentials.

---

## 📁 Project Structure

```text
Car_Rental/
│
├── bicycle/                     # Core Django application
│   ├── migrations/              # Database migration files
│   ├── __init__.py
│   ├── admin.py                 # Admin panel configuration
│   ├── models.py                # Car & Booking database models
│   ├── views.py                 # Authentication & booking logic
│   └── urls.py                  # App-level URL routing
│
├── templates/                   # HTML templates
│   ├── index.html               # Homepage – car listings
│   ├── booking.html             # Car booking page
│   ├── login.html               # User login page
│   └── register.html            # User registration page
│
├── static/                      # Static assets
│   ├── css/                     # Stylesheets
│   ├── js/                      # JavaScript files
│   └── images/                  # Images (cars, logos, UI assets)
│
├── Car_Rental/                  # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py              # Project settings
│   ├── urls.py                  # Project-level URL routing
│   └── wsgi.py
│
├── db.sqlite3                   # SQLite database
├── manage.py                    # Django management script
└── README.md                    # Project documentation

```

---

## 📸 Screenshot

![GitHub Logo](https://github.com/raunakmallick18/car-rental/blob/main/DriveEase.png)
