# Shop Products API (WORK IN PROGRESS)

A Django REST API for shop products.

The purpose of this project is to demonstrate my skills
as well as compliance with best practices.

## Tech Stack

- Python 3.12
- Django 6.0
- Django REST Framework
- PostgreSQL 16
- Docker & Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose installed

### Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Django-ShopProductsAPI
   ```

2. **Create environment file**

   ```bash
   cp ShopProductsAPI/.env.example ShopProductsAPI/.env
   ```

3. **Start the services**

   ```bash
   docker compose up -d --build
   ```

4. **Run migrations**

   ```bash
   docker compose exec backend python manage.py migrate
   ```

5. **Create a superuser (optional)**

   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

6. **Access the application**
   - API: http://localhost:8000
   - Admin: http://localhost:8000/admin

## Useful Commands

### Docker

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Rebuild after changes
docker compose up -d --build

# Stop and remove volumes (clears database)
docker compose down -v
```

### Django

```bash
# Run migrations
docker compose exec backend python manage.py migrate

# Create migrations
docker compose exec backend python manage.py makemigrations

# Run tests
docker compose exec backend python manage.py test

# Access Django shell
docker compose exec backend python manage.py shell

# Create superuser
docker compose exec backend python manage.py createsuperuser
```

### Database

```bash
# Access PostgreSQL shell
docker compose exec db psql -U postgres -d shop_products

# Run a SQL query
docker compose exec db psql -U postgres -d shop_products -c "SELECT * FROM user_user;"
```

## Project Structure

```
django-api-example/
├── ShopProductsAPI/
│   ├── api/
│   │   └── user/           # User app
│   ├── shop_products_api/  # Project settings
│   └── .env                # Environment variables
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Environment Variables

| Variable            | Description       | Default         |
| ------------------- | ----------------- | --------------- |
| `SECRET_KEY`        | Django secret key | -               |
| `DEBUG`             | Debug mode        | `True`          |
| `POSTGRES_DB`       | Database name     | `shop_products` |
| `POSTGRES_USER`     | Database user     | `postgres`      |
| `POSTGRES_PASSWORD` | Database password | `postgres`      |
| `POSTGRES_HOST`     | Database host     | `localhost`     |
| `POSTGRES_PORT`     | Database port     | `5432`          |
