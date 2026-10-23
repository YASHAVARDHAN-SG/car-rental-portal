# 🚗 DriveEase - Car Rental Management System

A full-stack **Car Rental Management System** built using **Django**, featuring user authentication, car booking, admin management, and dynamic price calculation. This project is suitable for academic submissions, portfolio showcasing, and real-world learning.

---

## 📌 Features

### 👤 Authentication
- User Registration
- User Login & Logout
- Session-based authentication
- Protected routes using `@login_required`

### 🚘 Car Management
- Add, update, and delete cars via Admin Panel
- Set car availability
- Price per day configuration

### 📅 Booking System
- Book cars by selecting start and end dates
- Automatic total price calculation
- User-specific bookings
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

CircleCI builds the Docker image, runs the Django unit-test job, and only then pushes the saved image to ECR. The deploy job runs after a successful push on `main`. The build image is passed between jobs using a CircleCI workspace so the tested commit's image is the one published.

## Deploy to EC2 with Docker and ECR

The repository `Dockerfile` builds the Django runtime image. The `build-image` and `unit-tests` jobs run before `push-image`; the latter assumes the AWS role through OIDC and publishes the image to ECR. Deployment is restricted to the `main` branch.

### One-time AWS and EC2 setup

1. Create an ECR repository in the same AWS region as the EC2 instance. Set `ECR_REPOSITORY` to its repository name (not the full registry URI).
2. Configure the IAM role `arn:aws:iam::027401589480:role/Githubcirclecicarrental` to trust CircleCI's OIDC identity provider for this CircleCI organization and project. Limit the trust policy to this project and grant the role only the ECR permissions needed to authenticate and push to the application repository. The deploy job exchanges CircleCI's OIDC token for temporary role credentials; it does not use IAM user access keys. If this role currently trusts GitHub Actions, add/configure CircleCI's OIDC provider and trust policy as well—GitHub's OIDC token cannot be used by CircleCI.
3. Attach an instance profile to EC2 that includes `AmazonSSMManagedInstanceCore` and ECR pull permissions (for example, `AmazonEC2ContainerRegistryReadOnly`). Ensure the SSM Agent is installed and the instance is online in Systems Manager. Docker must already be installed, and the instance needs outbound HTTPS access to SSM, ECR, and package repositories (or corresponding VPC endpoints). Separately, the CircleCI OIDC role also needs `ssm:SendCommand` permission scoped to this EC2 instance and the `AWS-RunShellScript` document, plus `ssm:GetCommandInvocation`. The deploy script installs and configures Nginx as the default port-80 site on this dedicated instance, proxying to the app container on `127.0.0.1:8000`; it replaces the enabled Nginx `default` site. Configure the instance security group to allow HTTP on port 80. SSH is not used; port 22 can remain closed. Do not expose port 8000 publicly.
4. Create the Compose working directory and environment file in the Ubuntu user's home directory on EC2. The deployment should run Compose from `~/car-rental`; the `docker-compose.prod.yml` file is copied there on each deployment, while `.env` is created once and kept out of source control:

   ```bash
   mkdir -p ~/car-rental/data
   tee ~/car-rental/.env >/dev/null <<'EOF'
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=replace-with-a-long-random-secret
   DJANGO_ALLOWED_HOSTS=your-ec2-public-dns,your-domain.example
   EOF
   chmod 600 ~/car-rental/.env
   ```

   Replace the example secret and hosts before deployment. Keep this file on the instance; do not commit it. Compose sets `DJANGO_DB_PATH=/app/data/db.sqlite3`; SQLite data persists in `~/car-rental/data` across container replacements. The deployment script must export `APP_IMAGE` to the full ECR image URI before running `docker compose -f docker-compose.prod.yml up -d`.
5. Add these CircleCI project environment variables. Do not put secret values in the repository:

   | Variable | Value |
   | --- | --- |
   | `ECR_REPOSITORY` | Existing ECR repository name |
   | `EC2_INSTANCE_ID` | EC2 instance ID, for example `i-0123456789abcdef0` |
CircleCI does not use GitHub Actions' `permissions: id-token: write` syntax. It provides `CIRCLE_OIDC_TOKEN_V2` to jobs automatically; the `deploy-ec2` job exchanges that token for temporary AWS credentials. The workflow already restricts deployment to `main`; the IAM role trust policy should independently restrict access to the CircleCI project, this repository, and the `main` ref. Use `github.com/YASHAVARDHAN-SG/car-rental-portal` as this repository's VCS origin, not the `portfolo` repository from the separate GitHub Actions example.

The role ARN is configured in the `deploy-ec2` job in `.circleci/config.yml`. The CircleCI role needs ECR image-push permission and SSM `SendCommand`/`GetCommandInvocation` permissions described above. No AWS IAM user keys or SSH private keys should be added to CircleCI. In the role trust policy, use the CircleCI OIDC provider URL `https://oidc.circleci.com/org/<CIRCLECI_ORG_ID>` and set the provider audience to the CircleCI organization UUID. Restrict the trust policy to this project's CircleCI project UUID and the `main` branch. For example, the `Condition` for a CircleCI V2 token can use:

```json
{
  "StringEquals": {
    "oidc.circleci.com/org/<CIRCLECI_ORG_ID>:aud": "<CIRCLECI_ORG_ID>"
  },
  "StringLike": {
    "oidc.circleci.com/org/<CIRCLECI_ORG_ID>:sub": "org/<CIRCLECI_ORG_ID>/project/<CIRCLECI_PROJECT_ID>/user/*/vcs-origin/github.com/YASHAVARDHAN-SG/car-rental-portal/vcs-ref/refs/heads/main"
  }
}
```

Replace both placeholders with IDs from CircleCI organization and project settings. Ensure the IAM OIDC provider and role trust policy match the token version used by the job.

The AWS region is set to `us-east-1` in the CircleCI deploy job to match the reference workflow. If the ECR repository or EC2 instance is in another region, change `AWS_DEFAULT_REGION` in `.circleci/config.yml` to that region.

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
