from app import app, db

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Only enable debug mode in development
    # Set FLASK_ENV=production and FLASK_DEBUG=False for production deployment
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
