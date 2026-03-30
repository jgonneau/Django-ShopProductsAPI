# Shop Products API (WORK IN PROGRESS)

A Django REST API for shop products.

The purpose of this project is to demonstrate my skills
as well as compliance with best practices.

## Tech Stack

- Python 3.12
- Django 6.0
- Django REST Framework
- drf-spectacular (OpenAPI/Swagger documentation)
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
   - API Documentation (Swagger): http://localhost:8000/api/docs/
   - API Documentation (ReDoc): http://localhost:8000/api/redoc/
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
│   │   ├── admin/          # Admin-only API endpoints
│   │   ├── invoice/        # Invoice management
│   │   ├── log/            # System logging
│   │   ├── order/          # Order management
│   │   ├── product/        # Product catalog
│   │   ├── store/          # Store management
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

- `POST /api/user/register/` - User registration
- `GET /api/products/public/` - List available products
- `GET /api/stores/public/` - List stores

### Authenticated User Endpoints

- `GET /api/user/me/` - Get current user profile
- `PATCH /api/user/me/` - Update profile
- `POST /api/user/change-password/` - Change password
- `GET /api/orders/` - List user's orders
- `POST /api/orders/` - Create new order
- `GET /api/invoices/` - List user's invoices

### Store Owner Endpoints

- `GET /api/stores/` - List owned stores
- `POST /api/stores/` - Create new store
- `GET /api/products/` - List products in owned stores
- `POST /api/products/store/<store_id>/` - Add product to store

### Admin Endpoints (`/api/admin/`)

- Full CRUD for users, stores, products, orders, invoices
- Log management and statistics

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
