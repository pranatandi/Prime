# 🌴 Palm Fruit Weighing System (Prime)

A complete workflow management system for palm fruit weighing operations with QR/Barcode scanning, USB/Serial scale integration, and automated slip generation.

## Features

- **QR/Barcode Scanning**: Fast vehicle enqueuing via DO Number scan
- **USB/Serial Scale Integration**: Automatic weight reading from digital scale indicators
- **Complete Workflow Management**: From entry to exit with status tracking
- **Deduction/Sorting Management**: Record quality deductions during inspection
- **Automated Calculations**: Net weight and final weight after deductions
- **Slip Generation**: Print-ready weighing slips with complete details
- **Audit Trail**: Full tracking of all status changes and modifications
- **Mock Mode**: Test without hardware using simulated weights

## Workflow

1. **QR/Barcode Scan** - Vehicle arrives and DO Number is scanned to enqueue
2. **Gross Weighing** - System reads gross weight (bruto) from scale via USB/Serial
3. **Sorting** - Staff enters deductions (potongan) after inspection
4. **Tare Weighing** - System reads tare weight (tarra) from scale
5. **Slip Generation** - Complete weighing slip is generated and printed

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- USB/Serial scale indicator (optional - can use mock mode for testing)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/pranatandi/Prime.git
cd Prime
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create environment configuration:
```bash
cp .env.example .env
```

4. Edit `.env` file to configure your settings:
```bash
# For testing without hardware, keep MOCK_SERIAL=True
MOCK_SERIAL=True

# For production with real scale, set MOCK_SERIAL=False and configure serial port
# MOCK_SERIAL=False
# SERIAL_PORT=/dev/ttyUSB0
# SERIAL_BAUDRATE=9600
```

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to:
```
http://localhost:5000
```

## Hardware Integration

### Supported Scale Indicators

The system is designed to work with common digital scale indicators that communicate via USB/Serial (RS-232). It supports various output formats including:

- `ST,GS,+12345.67kg\r\n`
- `+12345.67\r\n`
- `WT:12345.67\r\n`

### Serial Port Configuration

Configure the serial port settings in the `.env` file:

```bash
# Serial Port Configuration
SERIAL_PORT=/dev/ttyUSB0        # COM port (e.g., COM1 on Windows, /dev/ttyUSB0 on Linux)
SERIAL_BAUDRATE=9600            # Baud rate (common: 9600, 4800, 2400)
SERIAL_BYTESIZE=8               # Data bits (usually 8)
SERIAL_PARITY=N                 # Parity (N=None, E=Even, O=Odd)
SERIAL_STOPBITS=1               # Stop bits (usually 1)
SERIAL_TIMEOUT=1                # Timeout in seconds
```

### Finding Your Serial Port

**Windows:**
- Check Device Manager → Ports (COM & LPT)
- Look for "USB Serial Port (COMx)"

**Linux:**
```bash
# List USB serial devices
ls /dev/ttyUSB*

# Or check all serial ports
dmesg | grep tty
```

**macOS:**
```bash
ls /dev/cu.*
```

### Testing Scale Connection

1. Use the built-in test on the home page
2. Or test via command line:
```bash
python -c "from app.scale_reader import ScaleReader; reader = ScaleReader(); reader.test_connection()"
```

## Database Schema

### DO Numbers
- `do_number`: Unique delivery order identifier
- `supplier_name`: Supplier information
- `vehicle_number`: Vehicle registration
- `driver_name`: Driver information
- `is_active`: Active status flag

### Weighing Transactions
- `do_number_id`: Reference to DO Number
- `status`: Current workflow status (waiting_gross, sorting, waiting_tare, completed)
- `gross_weight`, `gross_time`: Entry weight and timestamp
- `tare_weight`, `tare_time`: Exit weight and timestamp
- `net_weight`: Calculated gross - tare
- `total_deduction`: Sum of all deductions
- `net_after_deduction`: Final weight after deductions

### Deductions
- `transaction_id`: Reference to transaction
- `deduction_type`: Type of deduction (damaged, unripe, etc.)
- `amount`: Deduction amount in kg
- `remarks`: Additional notes
- `sorting_time`: When deduction was recorded

### Audit Logs
- Complete tracking of all changes and status transitions
- Records action, old value, new value, description, and user

## API Endpoints

### DO Number Management
- `GET /api/do-numbers` - List all active DO numbers
- `POST /api/do-numbers` - Create new DO number

### Workflow Operations
- `POST /api/scan` - Scan DO number and enqueue vehicle
- `POST /api/transactions/{id}/gross-weight` - Record gross weight
- `POST /api/transactions/{id}/deductions` - Add deduction
- `POST /api/transactions/{id}/complete-sorting` - Complete sorting phase
- `POST /api/transactions/{id}/tare-weight` - Record tare weight
- `GET /api/transactions/{id}` - Get transaction details
- `GET /api/transactions` - List all transactions

### Utility
- `GET /api/scale/test` - Test scale connection

## Usage Guide

### 1. Initial Setup

Create test DO numbers via the scan page using "Create Test DO" button, or via API:

```bash
curl -X POST http://localhost:5000/api/do-numbers \
  -H "Content-Type: application/json" \
  -d '{"do_number": "DO12345", "supplier_name": "ABC Supplier", "vehicle_number": "B1234XYZ"}'
```

### 2. Vehicle Entry (Scan)

Navigate to **Scan DO** page and scan or enter the DO Number. This creates a new transaction with status `waiting_gross`.

### 3. Gross Weighing

From the **Queue** page:
1. Find the transaction with status "waiting_gross"
2. Click "Record Gross Weight"
3. System automatically reads weight from scale
4. Status changes to "sorting"

### 4. Sorting/Deductions

From the **Queue** page:
1. Click "Sorting" button for transaction
2. Add deductions as needed:
   - Select deduction type
   - Enter amount in kg
   - Add remarks (optional)
3. Click "Complete Sorting" when done
4. Status changes to "waiting_tare"

### 5. Tare Weighing

From the **Queue** page:
1. Find the transaction with status "waiting_tare"
2. Click "Record Tare Weight"
3. System automatically reads weight from scale
4. Weights are calculated automatically
5. Status changes to "completed"

### 6. View/Print Slip

From the **Queue** page:
1. Click "View Slip" for completed transaction
2. Review all details
3. Click "Print Slip" to print

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=app
```

### Mock Mode for Development

When `MOCK_SERIAL=True`, the system generates realistic random weights:
- Gross weight: 15,000 - 30,000 kg
- Tare weight: 8,000 - 12,000 kg

This allows full testing without physical scale hardware.

### Customizing Scale Protocol

If your scale uses a different protocol, modify the `_parse_weight_from_response()` method in `app/scale_reader.py`:

```python
def _parse_weight_from_response(self, response):
    # Add your custom parsing logic here
    # Return weight as float in kg
    pass
```

## Troubleshooting

### Scale Not Responding

1. Check serial port connection: `ls /dev/ttyUSB*` (Linux) or Device Manager (Windows)
2. Verify serial port settings match your scale's configuration
3. Check cable connections
4. Test with mock mode first to verify software is working
5. Some scales require a command to trigger output - uncomment the write line in `_read_real_weight()`

### Permission Denied on Serial Port (Linux)

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Or set port permissions
sudo chmod 666 /dev/ttyUSB0
```

### Database Issues

Delete the database file to reset:
```bash
rm weighing_system.db
python app.py  # Will recreate tables
```

## Production Deployment

### Security Considerations

1. Change the `SECRET_KEY` in `.env` to a strong random value
2. Set `FLASK_ENV=production` and `FLASK_DEBUG=False`
3. Use a production database (PostgreSQL, MySQL) instead of SQLite
4. Set up proper authentication and authorization
5. Use HTTPS in production

### Using PostgreSQL

1. Install psycopg2: `pip install psycopg2-binary`
2. Update `.env`:
```bash
DATABASE_URL=postgresql://user:password@localhost/weighing_db
```

### Running with Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.