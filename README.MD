# Shop Products API

A Django REST API for an online shop's products.

The purpose of this project is to demonstrate my skills
as well as compliance with best practices.

## Tech Stack

- Python 3.12
- Django 6.0
- Django REST Framework
- [djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/) (JWT authentication)
- drf-spectacular (OpenAPI / Swagger / ReDoc)
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
   - API : http://localhost:8000 → `/api/docs/`
   - API Documentation (Swagger): http://localhost:8000/api/docs/
   - API Documentation (ReDoc): http://localhost:8000/api/redoc/
   - OpenAPI schema (JSON): http://localhost:8000/api/schema/
   - Admin: http://localhost:8000/admin

### Authentication

- **Development** (`DJANGO_ENV=dev`, default): JWT (`Authorization: Bearer <access>`), plus Basic and Session auth for the browsable API.

- **Production** (`DJANGO_ENV=prod`): JWT only (no Basic/Session). Requires `rest_framework_simplejwt.token_blacklist` migrations—run `migrate` after switching to prod the first time.

Obtain tokens with `POST /api/user/login/` using JSON body `{"email": "...", "password": "..."}`
Refresh with `POST /api/user/token/refresh/` and verify with `POST /api/user/token/verify/`.

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

### Django (backend)

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

# Seed the database with static data
docker compose exec backend python manage.py seed_data

# Clear existing data and re-seed
docker compose exec backend python manage.py seed_data --clear

# OR populate database with factories
# Basic usage (creates 1 user, 1 admin, 1 store, 5 products)
docker compose exec backend python manage.py seed_factories

# Custom quantities
docker compose exec backend python manage.py seed_factories --users=3 --admins=2 --stores=2 --products=10
```

### Database (db)

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
│   │   ├── admin/          # Admin-only API endpoints
│   │   ├── log/            # System logging
│   │   ├── product/        # Product catalog
│   │   ├── store/          # Store management
│   │   ├── order/          # Order management
│   │   ├── invoice/        # Invoice management
│   │   └── user/           # User authentication & management
│   ├── shop_products_api/  # Project settings
│   └── .env                # Environment variables
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## API Modules

| Module    | Description                                           |
| --------- | ----------------------------------------------------- |
| `user`    | User registration, authentication, profile management |
| `store`   | Store creation and management for vendors             |
| `product` | Product catalog with stock management                 |
| `order`   | Customer order processing and tracking                |
| `invoice` | Invoice generation and payment status                 |
| `log`     | System logging and audit trail (admin only)           |

## API Endpoints

### Public Endpoints

- `POST /api/user/register/` — User registration
- `POST /api/user/login/` — JWT access + refresh tokens (body: `email`, `password`)
- `POST /api/user/token/refresh/` — New access token (body: `refresh`)
- `POST /api/user/token/verify/` — Validate a token (body: `token`)
- `GET /api/products/` — List available products
- `GET /api/stores/` — List stores

### Authenticated User Endpoints

Send `Authorization: Bearer <access_token>`

- `GET /api/user/` — Current user profile
- `PATCH /api/user/` — Update profile
- `POST /api/user/change-password/` — Change password
- `POST /api/user/delete/` — Delete own account (body includes password per serializer)
- `GET /api/orders/` — List user's orders
- `POST /api/orders/` — Create order
- `GET /api/invoices/` — List user's invoices

### Store Owner Endpoints

- `GET /api/stores/` - List owned stores
- `POST /api/stores/` - Create new store
- `GET /api/products/` - List products in owned stores
- `POST /api/products/store/<store_id>/` - Add product to store

### Admin Endpoints (`/api/admin/`)

- Full CRUD for users, stores, products, orders, invoices
- Log management and statistics

## Environment Variables

Copy `ShopProductsAPI/.env.example` to `ShopProductsAPI/.env` and adjust values.

| Variable              | Description                          | Default / notes        |
| --------------------- | ------------------------------------ | ---------------------- |
| `SECRET_KEY`          | Django secret key                    | Required in production |
| `DEBUG`               | Debug mode                           | `True` in example      |
| `DJANGO_ENV`          | `dev` or `prod`                      | `dev`                  |
| `ALLOWED_HOSTS`       | Comma-separated hosts (used in prod) | Empty if unset         |
| `SECURE_SSL_REDIRECT` | Force HTTPS (prod)                   | `True` if unset        |
| `POSTGRES_DB`         | Database name                        | `shop_products`        |
| `POSTGRES_USER`       | Database user                        | `postgres`             |
| `POSTGRES_PASSWORD`   | Database password                    | `postgres`             |
| `POSTGRES_HOST`       | Database host (`db` in Compose)      | `localhost` locally    |
| `POSTGRES_PORT`       | Database port                        | `5432`                 |

Note: In Docker Compose, the backend typically uses `POSTGRES_HOST=db`
(set in compose env, not only `.env`).
