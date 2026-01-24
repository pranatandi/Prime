# Prime - Palm Fruit Weighing System

A modern, Progressive Web App (PWA) for managing palm fruit weighing operations built with Laravel framework, featuring gRPC integration, comprehensive audit trails, and offline capabilities.

## 🌟 Features

### Core Features
- **Weighing Management**: Complete CRUD operations for weighing transactions with auto-calculation of net weight
- **Master Data Management**: Suppliers, vehicles, and user management with role-based access
- **Dashboard & Reporting**: Real-time statistics, charts, and export to Excel
- **Audit Trail System**: Comprehensive activity logging powered by Spatie Activity Log
- **Multi-language Support**: English and Bahasa Indonesia

### Technical Features
- **Progressive Web App (PWA)**: 
  - Offline capability with service worker
  - Installable on mobile and desktop
  - Push notifications support
  - Background sync for offline transactions
- **gRPC Integration**: Ready for communication with weighing scale devices and microservices
- **Security**: CSRF protection, SQL injection prevention, XSS protection, rate limiting
- **Modern UI**: Responsive design (mobile & desktop ready)

## 📋 Requirements

- PHP 8.2 or higher
- Composer
- Node.js & NPM
- MySQL 5.7+ / PostgreSQL 12+ / SQLite
- Redis (optional, for caching and queues)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/pranatandi/Prime.git
cd Prime
```

### 2. Install Dependencies
```bash
# Install PHP dependencies
composer install

# Install JavaScript dependencies
npm install
```

### 3. Environment Configuration
```bash
# Copy environment file
cp .env.example .env

# Generate application key
php artisan key:generate

# Configure your database in .env
# For MySQL:
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=prime_weighing
DB_USERNAME=root
DB_PASSWORD=your_password
```

### 4. Database Setup
```bash
# Run migrations
php artisan migrate

# Seed database with sample data
php artisan db:seed
```

### 5. Storage Setup
```bash
# Create storage link for file uploads
php artisan storage:link
```

### 6. Publish Package Assets
```bash
# Publish activity log migrations and config
php artisan vendor:publish --provider="Spatie\Activitylog\ActivitylogServiceProvider" --tag="activitylog-migrations"
php artisan vendor:publish --provider="Spatie\Activitylog\ActivitylogServiceProvider" --tag="activitylog-config"

# Publish Excel config (optional)
php artisan vendor:publish --provider="Maatwebsite\Excel\ExcelServiceProvider" --tag="config"
```

### 7. Build Assets
```bash
# Development
npm run dev

# Production
npm run build
```

### 8. Start the Application
```bash
# Start Laravel development server
php artisan serve

# Or use Laravel Sail (Docker)
./vendor/bin/sail up
```

Visit: `http://localhost:8000`

## 👤 Default Users

After seeding, you can login with these credentials:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@prime.com | password |
| Operator | operator@prime.com | password |
| Viewer | viewer@prime.com | password |

## 📁 Project Structure

```
prime/
├── app/
│   ├── Http/Controllers/
│   │   ├── DashboardController.php
│   │   ├── WeighingController.php
│   │   ├── SupplierController.php
│   │   └── VehicleController.php
│   ├── Models/
│   │   ├── User.php
│   │   ├── Weighing.php
│   │   ├── Supplier.php
│   │   └── Vehicle.php
│   ├── Services/
│   │   ├── GrpcService.php
│   │   └── ReportService.php
│   └── Traits/
│       └── Auditable.php
├── database/
│   ├── migrations/
│   └── seeders/
├── public/
│   ├── manifest.json          # PWA manifest
│   ├── sw.js                  # Service Worker
│   ├── offline.html           # Offline fallback page
│   └── icons/                 # PWA icons
├── proto/
│   └── weighing.proto         # gRPC protocol definitions
├── resources/
│   ├── views/
│   └── js/
│       └── pwa.js            # PWA registration script
└── routes/
    ├── web.php
    └── api.php
```

## 🔧 Configuration

### Database
Edit `.env` file to configure your database connection:
- MySQL/MariaDB (recommended for production)
- PostgreSQL
- SQLite (good for development)

### gRPC
Configure gRPC endpoints in `.env`:
```env
GRPC_SERVER_HOST=0.0.0.0
GRPC_SERVER_PORT=50051
GRPC_SCALE_ENDPOINT=127.0.0.1:50052
```

### PWA
Enable/disable PWA features in `.env`:
```env
PWA_ENABLED=true
```

### Activity Logs
Configure audit trail retention:
```env
ACTIVITY_LOG_ENABLED=true
ACTIVITY_LOG_DELETE_RECORDS_OLDER_THAN_DAYS=365
```

## 📱 PWA Features

### Installation
Users can install the app on their devices:
- **Desktop**: Click the install button in the address bar
- **Mobile**: Add to Home Screen from browser menu

### Offline Mode
- Static assets are cached for offline access
- Recent weighing data can be viewed offline
- Transactions made offline are synced when connection is restored

### Push Notifications
Enable notifications to receive alerts for:
- New weighing transactions
- System alerts
- Daily reports

## 🔐 Security Features

- **Authentication**: Laravel Sanctum/Breeze ready
- **Authorization**: Role-based access control (Admin, Operator, Viewer)
- **CSRF Protection**: All forms are CSRF protected
- **SQL Injection Prevention**: Using Eloquent ORM and prepared statements
- **XSS Protection**: Input sanitization and output escaping
- **Rate Limiting**: Configurable per-minute request limits
- **Audit Trail**: All user activities are logged

## 🧪 Testing

```bash
# Run all tests
php artisan test

# Run specific test suite
php artisan test --testsuite=Feature

# Run with coverage
php artisan test --coverage
```

## 📊 Usage

### Creating Weighing Transaction
1. Navigate to Weighing → Create New
2. Select supplier and vehicle
3. Enter gross weight and tare weight (net weight is calculated automatically)
4. Upload vehicle photo (optional)
5. Add notes if needed
6. Save transaction

### Viewing Reports
1. Go to Dashboard
2. View daily/monthly statistics
3. Export reports to Excel or PDF
4. Filter by date range, supplier, or vehicle

### Managing Master Data
- **Suppliers**: Add/edit supplier information
- **Vehicles**: Register and manage vehicles
- **Users**: Manage user accounts and roles (Admin only)

## 🛠 Development

### Code Standards
This project follows PSR-12 coding standards.

### Running Linter
```bash
# Check code style
./vendor/bin/pint --test

# Fix code style
./vendor/bin/pint
```

### Queue Workers
For background jobs:
```bash
php artisan queue:work
```

## 🌐 Localization

Add new languages:
1. Create language files in `resources/lang/`
2. Update `SUPPORTED_LOCALES` in `.env`
3. Translate strings in views and controllers

## 📦 Deployment

### Production Checklist
- [ ] Set `APP_ENV=production` in `.env`
- [ ] Set `APP_DEBUG=false` in `.env`
- [ ] Configure proper database credentials
- [ ] Run `php artisan config:cache`
- [ ] Run `php artisan route:cache`
- [ ] Run `php artisan view:cache`
- [ ] Set up queue worker as system service
- [ ] Configure SSL certificate
- [ ] Set up automated backups
- [ ] Configure proper file permissions

### Server Requirements
- PHP-FPM or PHP with Apache/Nginx
- MySQL/PostgreSQL database server
- Redis (recommended for caching and queues)
- Supervisor for queue workers
- SSL certificate for HTTPS (required for PWA features)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Support

For support, email support@prime.com or open an issue in the repository.

## 🙏 Acknowledgments

- Laravel Framework
- Spatie Activity Log
- Maatwebsite Excel
- Google Protocol Buffers
- And all other open source contributors

---

Made with ❤️ for the palm oil industry
