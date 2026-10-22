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

CircleCI runs the `build`, `test`, `sonarqube-analysis`, and `security-scan` jobs on commits and pull-request branches. After those checks pass, the `deploy-ec2` job runs only on `main`: CircleCI assumes an AWS role through OIDC, builds and pushes the app image to Amazon ECR, and deploys it to EC2 through AWS Systems Manager (SSM). The EC2 instance pulls the image using its instance role and configures host-level Nginx to proxy HTTP traffic to the app container. The container port is bound to EC2 localhost only. High- and critical-severity Trivy findings fail the scan. Configure `SONAR_HOST_URL`, `SONAR_TOKEN`, and `SONAR_PROJECT_KEY` as CircleCI project environment variables for SonarQube. Build, test, and security-scan logs are uploaded as artifacts.

## Deploy to EC2 with Docker and ECR

The repository `Dockerfile` builds the Django runtime image. CircleCI continues to use its own Python, SonarQube, and Trivy images for CI; the deploy job builds the application image and stores that image in ECR. Deployment is restricted to the `main` branch.

### One-time AWS and EC2 setup

1. Create an ECR repository in the same AWS region as the EC2 instance. Set `ECR_REPOSITORY` to its repository name (not the full registry URI).
2. Configure the IAM role `arn:aws:iam::027401589480:role/Githubcirclecicarrental` to trust CircleCI's OIDC identity provider for this CircleCI organization and project. Limit the trust policy to this project and grant the role only the ECR permissions needed to authenticate and push to the application repository. The deploy job exchanges CircleCI's OIDC token for temporary role credentials; it does not use IAM user access keys. If this role currently trusts GitHub Actions, add/configure CircleCI's OIDC provider and trust policy as well—GitHub's OIDC token cannot be used by CircleCI.
3. Attach an instance profile to EC2 that includes `AmazonSSMManagedInstanceCore` and ECR pull permissions (for example, `AmazonEC2ContainerRegistryReadOnly`). Ensure the SSM Agent is installed and the instance is online in Systems Manager. Docker must already be installed, and the instance needs outbound HTTPS access to SSM, ECR, and package repositories (or corresponding VPC endpoints). Separately, the CircleCI OIDC role also needs `ssm:SendCommand` permission scoped to this EC2 instance and the `AWS-RunShellScript` document, plus `ssm:GetCommandInvocation`. The deploy script installs and configures Nginx as the default port-80 site on this dedicated instance, proxying to the app container on `127.0.0.1:8000`; it replaces the enabled Nginx `default` site. Configure the instance security group to allow HTTP on port 80. SSH is not used; port 22 can remain closed. Do not expose port 8000 publicly.
4. Create the app's persistent data directory and environment file on EC2:

   ```bash
   sudo mkdir -p /opt/car-rental/data
   sudo tee /opt/car-rental/.env >/dev/null <<'EOF'
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=replace-with-a-long-random-secret
   DJANGO_ALLOWED_HOSTS=your-ec2-public-dns,your-domain.example
   DJANGO_DB_PATH=/app/data/db.sqlite3
   EOF
   sudo chmod 600 /opt/car-rental/.env
   ```

   Replace the example secret and hosts before deployment. Keep this file on the instance; do not commit it. SQLite data is persisted in `/opt/car-rental/data` across container replacements.
5. Add these CircleCI project environment variables. Do not put secret values in the repository:

   | Variable | Value |
   | --- | --- |
   | `AWS_DEFAULT_REGION` | ECR and EC2 AWS region |
   | `ECR_REPOSITORY` | Existing ECR repository name |
   | `EC2_INSTANCE_ID` | EC2 instance ID, for example `i-0123456789abcdef0` |
   | `SONAR_HOST_URL` | SonarQube server URL |
   | `SONAR_TOKEN` | SonarQube analysis token |
   | `SONAR_PROJECT_KEY` | SonarQube project key |

The role ARN is configured in the `deploy-ec2` job in `.circleci/config.yml`. The CircleCI role needs ECR image-push permission and SSM `SendCommand`/`GetCommandInvocation` permissions described above. No AWS IAM user keys or SSH private keys should be added to CircleCI. For the trust policy, use the CircleCI OIDC provider URL and audience for your CircleCI organization, and restrict the subject claim to this project's CircleCI project UUID. The organization ID and project UUID are available in CircleCI project/organization settings; they are specific to your account and are intentionally not guessed here.

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
