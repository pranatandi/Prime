# Prime Weighing System - API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently using Laravel session authentication. For API usage, consider implementing Laravel Sanctum or Passport.

## Routes Overview

### Web Routes

#### Dashboard
- **GET** `/dashboard` - View dashboard with statistics
  - Returns: Dashboard view with daily stats, chart data, and top suppliers

#### Weighing Transactions

- **GET** `/weighing` - List all weighing transactions
  - Query params:
    - `page` (int): Page number for pagination
  - Returns: List of weighing transactions with pagination (15 per page)

- **GET** `/weighing/create` - Show create weighing form
  - Returns: Form view with suppliers and vehicles dropdowns

- **POST** `/weighing` - Store new weighing transaction
  - Body params:
    - `supplier_id` (required|exists:suppliers,id)
    - `vehicle_id` (required|exists:vehicles,id)
    - `vehicle_plate_number` (required|string)
    - `gross_weight` (required|numeric|min:0)
    - `tare_weight` (required|numeric|min:0)
    - `weighing_datetime` (required|date)
    - `vehicle_photo` (nullable|image|max:2048)
    - `notes` (nullable|string)
  - Auto-generates:
    - `transaction_code`: Format WGH-YYYYMMDD-XXXX
    - `net_weight`: Calculated as gross_weight - tare_weight
    - `user_id`: From authenticated user
  - Returns: Redirect to weighing.index with success message

- **GET** `/weighing/{id}` - Show single weighing transaction
  - Returns: Detailed view of weighing transaction

- **GET** `/weighing/{id}/edit` - Show edit weighing form
  - Returns: Edit form with current data

- **PUT/PATCH** `/weighing/{id}` - Update weighing transaction
  - Body params: Same as POST
  - Returns: Redirect to weighing.index with success message

- **DELETE** `/weighing/{id}` - Delete weighing transaction
  - Returns: Redirect to weighing.index with success message

#### Suppliers

- **GET** `/suppliers` - List all suppliers
  - Query params:
    - `page` (int): Page number for pagination
  - Returns: List of suppliers with pagination (15 per page)

- **GET** `/suppliers/create` - Show create supplier form

- **POST** `/suppliers` - Store new supplier
  - Body params:
    - `name` (required|string|max:255)
    - `code` (required|string|max:50|unique:suppliers)
    - `phone` (nullable|string|max:20)
    - `address` (nullable|string)
    - `email` (nullable|email|max:255)
    - `status` (required|in:active,inactive)
  - Auto-generates:
    - `code`: Format SUP-XXXX (if not provided)
  - Returns: Redirect to suppliers.index with success message

- **GET** `/suppliers/{id}` - Show single supplier

- **GET** `/suppliers/{id}/edit` - Show edit supplier form

- **PUT/PATCH** `/suppliers/{id}` - Update supplier
  - Body params: Same as POST (code must be unique except for current record)
  - Returns: Redirect to suppliers.index with success message

- **DELETE** `/suppliers/{id}` - Delete supplier
  - Validation: Cannot delete if supplier has weighing transactions
  - Returns: Redirect to suppliers.index with success or error message

#### Vehicles

- **GET** `/vehicles` - List all vehicles
  - Query params:
    - `page` (int): Page number for pagination
  - Returns: List of vehicles with pagination (15 per page)

- **GET** `/vehicles/create` - Show create vehicle form

- **POST** `/vehicles` - Store new vehicle
  - Body params:
    - `plate_number` (required|string|max:20|unique:vehicles)
    - `type` (nullable|string|max:50)
    - `driver_name` (nullable|string|max:255)
    - `driver_phone` (nullable|string|max:20)
    - `status` (required|in:active,inactive)
  - Returns: Redirect to vehicles.index with success message

- **GET** `/vehicles/{id}` - Show single vehicle

- **GET** `/vehicles/{id}/edit` - Show edit vehicle form

- **PUT/PATCH** `/vehicles/{id}` - Update vehicle
  - Body params: Same as POST (plate_number must be unique except for current record)
  - Returns: Redirect to vehicles.index with success message

- **DELETE** `/vehicles/{id}` - Delete vehicle
  - Validation: Cannot delete if vehicle has weighing transactions
  - Returns: Redirect to vehicles.index with success or error message

#### Audit Logs

- **GET** `/audit-logs` - View audit trail
  - Returns: List of all activities with user, action, timestamp, and changes
  - Powered by Spatie Activity Log

## Response Formats

### Success Response (Redirect)
Redirects to index page with flash message:
```php
session()->flash('success', 'Record created successfully');
```

### Error Response (Validation)
Returns back to form with validation errors:
```php
$errors = [
    'field_name' => ['Error message']
]
```

### Error Response (Deletion Constraint)
Redirects with error message:
```php
session()->flash('error', 'Cannot delete record with existing transactions');
```

## Database Schema

### Users Table
- `id` (bigint)
- `name` (string)
- `email` (string, unique)
- `email_verified_at` (timestamp, nullable)
- `password` (string)
- `role` (enum: admin, operator, viewer)
- `remember_token` (string, nullable)
- `timestamps`

### Suppliers Table
- `id` (bigint)
- `name` (string)
- `code` (string, unique)
- `phone` (string, nullable)
- `address` (string, nullable)
- `email` (string, nullable)
- `status` (enum: active, inactive)
- `timestamps`

### Vehicles Table
- `id` (bigint)
- `plate_number` (string, unique)
- `type` (string, nullable)
- `driver_name` (string, nullable)
- `driver_phone` (string, nullable)
- `status` (enum: active, inactive)
- `timestamps`

### Weighing Transactions Table
- `id` (bigint)
- `transaction_code` (string, unique)
- `supplier_id` (foreign key)
- `vehicle_id` (foreign key)
- `vehicle_plate_number` (string)
- `gross_weight` (decimal 10,2)
- `tare_weight` (decimal 10,2)
- `net_weight` (decimal 10,2)
- `weighing_datetime` (datetime)
- `vehicle_photo` (string, nullable)
- `notes` (text, nullable)
- `user_id` (foreign key)
- `timestamps`

### Activity Log Table (Spatie)
- `id` (bigint)
- `log_name` (string, nullable)
- `description` (text)
- `subject_type` (string, nullable)
- `subject_id` (bigint, nullable)
- `causer_type` (string, nullable)
- `causer_id` (bigint, nullable)
- `properties` (json, nullable)
- `batch_uuid` (uuid, nullable)
- `event` (string, nullable)
- `created_at` (timestamp)

## Services

### GrpcService
Located at `app/Services/GrpcService.php`

Methods:
- `getWeightFromScale(string $scaleId): array` - Get current weight from scale
- `sendTransactionToMicroservice(array $data): bool` - Send transaction to other services
- `checkScaleConnection(string $scaleId): bool` - Verify scale connection

### ReportService
Located at `app/Services/ReportService.php`

Methods:
- `getDailyStats(?string $date = null): array` - Get daily statistics
- `getMonthlyStats(int $year, int $month): array` - Get monthly statistics
- `getChartData(string $startDate, string $endDate): array` - Get chart data for period
- `getTopSuppliers(int $limit = 10)` - Get top suppliers by weight

## gRPC Integration

Protocol buffer definitions are in `proto/weighing.proto`

### Services Defined:
1. **WeighingScaleService** - For hardware communication
   - `GetWeight` - Get current weight reading
   - `StreamWeight` - Stream continuous weight readings
   - `TareScale` - Zero the scale
   - `HealthCheck` - Check scale status

2. **WeighingTransactionService** - For microservices
   - `CreateTransaction` - Create transaction
   - `GetTransaction` - Get transaction by ID
   - `ListTransactions` - List with filters
   - `UpdateTransaction` - Update transaction

## PWA Features

### Service Worker
Located at `public/sw.js`
- Caches static assets
- Provides offline functionality
- Background sync for offline transactions
- Push notification support

### Manifest
Located at `public/manifest.json`
- App name, icons, theme
- Makes app installable
- Shortcuts to common actions

### PWA Registration
Located at `resources/js/pwa.js`
- Registers service worker
- Handles install prompt
- Manages online/offline detection
- Push notification setup

## Testing

Run tests:
```bash
php artisan test
```

Test coverage:
- Weighing CRUD operations
- Supplier management
- Vehicle management
- Auto-calculations (net weight)
- Code generation
- Validation rules
- Deletion constraints

## Notes

- All forms include CSRF protection
- Rate limiting: 60 requests per minute (configurable in .env)
- File uploads limited to 2MB for vehicle photos
- Pagination: 15 items per page
- Activity logging automatically tracks all model changes
- All timestamps in UTC, displayed in user's timezone

## Future API Enhancements

Consider implementing:
- RESTful API endpoints with JSON responses
- API authentication (Laravel Sanctum)
- API versioning (v1, v2)
- API rate limiting per user
- Webhook notifications
- Batch operations
- Advanced filtering and search
- Data export endpoints (Excel, PDF)
