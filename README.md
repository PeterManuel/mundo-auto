# MundoAuto E-commerce System

A comprehensive e-commerce system for auto parts built with FastAPI, PostgreSQL, and modern Python technologies.

## Features

### User Module / Customer (Buyer)

1. **Authentication & Account**
   - User registration with email, password, phone number
   - Login/Logout functionality with JWT
   - Password recovery system
   - User profile management (name, phone, address, profile photo)
   - Login history tracking
   - Google authentication (fully implemented)
   - Facebook authentication (placeholder implementation)

2. **Shopping & Product Catalog**
   - Browse products by categories (Brakes, Engine, Suspension, etc.)
   - Search by part name, OE number, brand, model, or license plate
   - Filter by brand, model, engine type, year, compatibility
   - View detailed product information:
     - Name, reference, compatibility, manufacturer, price
     - Images, technical details, reviews/comments
   - Shopping cart functionality (add, update quantity, remove)
   - Checkout process with multiple payment methods
   - Shipping and billing address management
   - Order confirmation with order number

3. **Order Management**
   - View list of orders
   - View order details (status, products, individual and total prices)
   - Track order status (Processing, Shipped, Delivered, Cancelled)
   - Shipment tracking (placeholder implementation)
   - Order cancellation and returns within timeframe

4. **Other Customer Features**
   - Wishlist functionality
   - Product price comparison
   - Receive promotional notifications
   - Get recommendations for compatible car parts
   - Live chat with store support (placeholder implementation)

### Admin / Store Manager Dashboard

1. **Dashboard Overview**
   - Sales metrics and visualization
   - Total sales, inventory levels, order counts
   - Best-selling products and most active customers
   - Low stock notifications

2. **Product Management**
   - Add/edit/remove products
   - Manage product images and descriptions
   - Set prices, discounts and categories
   - Define product compatibility (make, model, year, engine)
   - Import/export catalog via CSV (placeholder implementation)
   - Inventory management

3. **Order Management**
   - View all orders
   - Update order status
   - View customer order history
   - Generate PDF invoices (placeholder implementation)

### Global System Features
   - View all orders
   - Manage product catalog
   - Edit promotional banners
   - Manage featured products
   - Generate reports (PDF/Excel placeholder)
   - Store account management

## Technology Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migration Tool**: Alembic
- **Authentication**: JWT with OAuth2
- **Dependency Management**: Poetry
- **Data Validation**: Pydantic
- **Image Processing**: Pillow
- **Documentation**: Swagger UI / ReDoc (auto-generated)

## System Requirements

- Python 3.10 or higher
- PostgreSQL 12 or higher
- At least 2GB RAM
- 10GB disk space (for application and database)

## Installation & Setup

### Prerequisites
- Python 3.10+
- PostgreSQL
- Poetry (Python package manager)

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/mundo_auto.git
cd mundo_auto
```

### Step 2: Install Dependencies
```bash
poetry install
```

### Step 3: Configure Environment Variables
Create a `.env` file in the root directory:
```
# Basic configuration
PROJECT_NAME=MundoAuto
PROJECT_VERSION=0.1.0

# Security
SECRET_KEY=your_secure_random_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=mundo_auto
POSTGRES_PORT=5432

# CORS settings
BACKEND_CORS_ORIGINS=["http://localhost:3000", "https://mundo-auto-1.onrender.com"]

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://mundo-auto-1.onrender.com/api/v1/auth/google/callback

# Uploads directory
UPLOAD_DIRECTORY=uploads
```

### Step 4: Create Database
```bash
# Using psql command line
createdb mundo_auto

# Or in PostgreSQL shell
psql -U postgres
CREATE DATABASE mundo_auto;
```

### Step 5: Run Database Migrations
```bash
poetry run alembic upgrade head
```

### Step 6: Start the Application
```bash
poetry run uvicorn app.main:app --reload
```

The API will be available at https://mundo-auto-1.onrender.com

### Step 7: Login with Demo Users

After initialization, you can log in with the following pre-configured users:

- **Admin User**:
  - Email: admin@mundoauto.com
  - Password: admin123

- **Demo User**:
  - Email: demo@mundoauto.com
  - Password: demo123

## API Documentation

- **Swagger UI**: Available at `/docs` endpoint
- **ReDoc**: Available at `/redoc` endpoint

## API Endpoints Overview

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/logout` - Logout user
- `POST /api/v1/auth/password-recovery` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password with token
- `GET /api/v1/auth/google/login` - Initiate Google OAuth login
- `GET /api/v1/auth/google/callback` - Handle Google OAuth callback
- `POST /api/v1/auth/google/token` - Exchange Google auth code for token (mobile/SPA)

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile
- `POST /api/v1/users/me/upload-avatar` - Upload profile image
- `GET /api/v1/users/me/login-history` - Get login history

### Products
- `GET /api/v1/products/` - List products with filters
- `GET /api/v1/products/{id}` - Get product details
- `GET /api/v1/products/categories/` - List categories
- `POST /api/v1/products/{id}/reviews` - Add product review
- `GET /api/v1/products/{id}/reviews` - Get product reviews

### Shopping Cart
- `GET /api/v1/cart/` - Get user's cart
- `POST /api/v1/cart/` - Add item to cart
- `PUT /api/v1/cart/{item_id}` - Update cart item
- `DELETE /api/v1/cart/{item_id}` - Remove item from cart
- `DELETE /api/v1/cart/` - Clear cart

### Orders
- `POST /api/v1/orders/` - Create order from cart
- `GET /api/v1/orders/` - List user orders
- `GET /api/v1/orders/{id}` - Get order details
- `PUT /api/v1/orders/{id}/cancel` - Cancel order

### Admin
- `GET /api/v1/admin/dashboard` - Get dashboard stats
- `GET /api/v1/admin/products` - List all products
- `POST /api/v1/admin/products` - Create product
- `PUT /api/v1/admin/products/{id}` - Update product
- `DELETE /api/v1/admin/products/{id}` - Delete product
- `GET /api/v1/admin/orders` - List all orders
- `PUT /api/v1/admin/orders/{id}/status` - Update order status
- `GET /api/v1/admin/banners` - List banners
- `POST /api/v1/admin/banners` - Create banner
- `PUT /api/v1/admin/banners/{id}` - Update banner

## Testing

Run tests with pytest:
```bash
poetry run pytest
```

## Troubleshooting

### Authentication Issues

If you encounter password verification errors like:
```
error reading bcrypt version
AttributeError: module 'bcrypt' has no attribute '__about__'
```
or
```
ValueError: password cannot be longer than 72 bytes
```

These are related to compatibility issues between newer versions of the bcrypt and passlib libraries. 
The application includes a fallback mechanism to handle this, allowing the demo users to log in
even if there are bcrypt version conflicts.

### Database Connection Issues

If you encounter database connection errors, verify:
1. PostgreSQL is running
2. Your .env file has the correct database credentials
3. The database specified in your connection string exists

Run this command to verify database connection:
```bash
poetry run python -c "from app.db.session import engine; print('Connection successful' if engine else 'Connection failed')"
```

### Testing Authentication

To verify that authentication is working properly without using the web interface:

1. Make sure the API server is running:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

2. In a new terminal, run the test login script:
   ```bash
   poetry run python test_login.py
   ```

This will attempt to login with both the admin and demo accounts and show if they're successful.

## Development

### Creating New Database Migrations
After modifying models:
```bash
poetry run alembic revision --autogenerate -m "Description of changes"
poetry run alembic upgrade head
```

### Code Formatting
```bash
poetry run black app/
poetry run isort app/
```

### Type Checking
```bash
poetry run mypy app/
```

## Deployment

### Using Docker
A Dockerfile is provided for containerized deployment. Build and run:
```bash
docker build -t mundo-auto .
docker run -p 8000:8000 --env-file .env mundo-auto
```

### Database Backups
Regular database backups are recommended:
```bash
pg_dump -U postgres mundo_auto > backup_$(date +%Y%m%d).sql
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors

- Pedro Domingos (Project Lead)

## Support

For issues, feature requests or support, please create an issue on the GitHub repository or contact support@mundoauto.com