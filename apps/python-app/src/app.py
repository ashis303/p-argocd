#!/usr/bin/env python3
"""
Simple Flask application for demonstrating GitOps with ArgoCD
This application demonstrates:
- Loading configuration from environment variables
- Reading secrets from mounted volumes (Azure Key Vault via CSI)
- Health check endpoints for Kubernetes probes
- Structured logging
"""

import os
import sys
import logging
from flask import Flask, jsonify, request
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration from environment variables (set via ConfigMap)
APP_ENV = os.getenv('APP_ENV', 'development')
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

# Secrets path (mounted from Azure Key Vault via CSI driver)
SECRETS_PATH = '/mnt/secrets'

def read_secret(secret_name):
    """
    Read a secret from the mounted secrets volume
    
    Args:
        secret_name: Name of the secret file (matches objectAlias in SecretProviderClass)
    
    Returns:
        Secret value as string, or None if not found
    """
    try:
        secret_file_path = os.path.join(SECRETS_PATH, secret_name)
        with open(secret_file_path, 'r') as f:
            secret_value = f.read().strip()
            logger.info(f"Successfully loaded secret: {secret_name}")
            return secret_value
    except FileNotFoundError:
        logger.error(f"Secret not found: {secret_name} at {SECRETS_PATH}")
        return None
    except Exception as e:
        logger.error(f"Error reading secret {secret_name}: {str(e)}")
        return None

@app.route('/')
def home():
    """
    Root endpoint - returns application info
    """
    return jsonify({
        'application': 'Python GitOps Demo',
        'version': APP_VERSION,
        'environment': APP_ENV,
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'running'
    })

@app.route('/health')
def health():
    """
    Health check endpoint for Kubernetes liveness probe
    Returns 200 OK if the application is healthy
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/ready')
def ready():
    """
    Readiness check endpoint for Kubernetes readiness probe
    Returns 200 OK if the application is ready to serve traffic
    Checks if required secrets are available
    """
    # Check if secrets are available
    db_connection = read_secret('db-connection-string')
    api_key = read_secret('api-key')
    
    if db_connection and api_key:
        return jsonify({
            'status': 'ready',
            'secrets_loaded': True,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    else:
        return jsonify({
            'status': 'not ready',
            'secrets_loaded': False,
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@app.route('/config')
def config():
    """
    Display current configuration (non-sensitive values only)
    Useful for debugging environment-specific configurations
    """
    return jsonify({
        'environment': APP_ENV,
        'version': APP_VERSION,
        'debug_mode': DEBUG_MODE,
        'secrets_path': SECRETS_PATH,
        'secrets_available': {
            'db-connection-string': os.path.exists(os.path.join(SECRETS_PATH, 'db-connection-string')),
            'api-key': os.path.exists(os.path.join(SECRETS_PATH, 'api-key'))
        }
    })

@app.route('/api/data')
def get_data():
    """
    Sample API endpoint that demonstrates using secrets
    In a real application, this would connect to a database
    """
    try:
        # Read database connection string from mounted secret
        db_connection = read_secret('db-connection-string')
        api_key = read_secret('api-key')
        
        if not db_connection or not api_key:
            return jsonify({
                'error': 'Required secrets not available'
            }), 500
        
        # Simulate database query (don't expose actual secrets!)
        return jsonify({
            'message': 'Data retrieved successfully',
            'environment': APP_ENV,
            'secrets_status': 'loaded',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in /api/data endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

if __name__ == '__main__':
    logger.info(f"Starting Python GitOps Demo Application")
    logger.info(f"Environment: {APP_ENV}")
    logger.info(f"Version: {APP_VERSION}")
    logger.info(f"Debug Mode: {DEBUG_MODE}")
    
    # Run Flask app
    # In production, use a WSGI server like Gunicorn
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=DEBUG_MODE
    )
