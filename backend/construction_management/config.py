import os
import secrets
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    # Secret Key - Use an environment variable or generate a secure key dynamically
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(16))  # Fallback to a random key if not in the .env

    # Database URI - Use environment variable for the database URI
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(os.getcwd(), 'data.db'))  # Fallback to SQLite for dev

    # Disabling track modifications to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email configuration - Store in environment variables for security
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')  # Fetch from .env
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # Fetch from .env
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')  # Use the same email as the sender

    # Frontend URL for CORS configuration
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

    # JWT settings (if any required here)
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')  # Store this in the .env for production

    # CORS Configuration - Load from environment variables
    CORS_ORIGINS = os.getenv(
        'CORS_ORIGINS',
        'http://localhost:5173,http://localhost:5000,http://127.0.0.1:5173,http://127.0.0.1:5000'
    ).split(',')
    CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS]  # Clean up whitespace

    # Flask environment configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Optionally, you could set up additional configuration settings if necessary

