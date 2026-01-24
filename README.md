# Prime

A Laravel 10 web application.

## Requirements

- PHP 8.1 or higher
- Composer
- MySQL or other database system
- Node.js & NPM (optional, for frontend assets)

## Installation

Follow these steps to set up the project locally:

### 1. Clone the repository

```bash
git clone https://github.com/pranatandi/Prime.git
cd Prime
```

### 2. Install PHP dependencies

```bash
composer install
```

### 3. Set up environment configuration

Copy the example environment file and configure your environment variables:

```bash
cp .env.example .env
```

Edit the `.env` file and configure your database settings:

```
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=your_database_name
DB_USERNAME=your_database_user
DB_PASSWORD=your_database_password
```

### 4. Generate application key

```bash
php artisan key:generate
```

### 5. Set up the database

Create a database that matches the name you configured in the `.env` file, then run the migrations:

```bash
php artisan migrate
```

### 6. Configure storage permissions

Ensure the storage and bootstrap/cache directories are writable:

```bash
chmod -R 775 storage bootstrap/cache
```

### 7. Run the application

Start the development server:

```bash
php artisan serve
```

The application will be available at `http://localhost:8000`.

## Optional: Frontend Assets

If you need to compile frontend assets:

```bash
npm install
npm run dev
```

## Testing

Run the test suite:

```bash
php artisan test
```

## License

This project is open-sourced software licensed under the [MIT license](https://opensource.org/licenses/MIT).