"""
Authentication API Endpoints
"""
from flask import Blueprint, request, jsonify, session, redirect
from backend.database.db import db
from backend.models.user import User
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


# -----------------------------
# User Registration
# -----------------------------
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    User registration endpoint
    
    Request body:
    {
        "email": "user@example.com",
        "password": "password123",
        "full_name": "John Doe",
        "role": "executive"
    }
    """
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('email') or not data.get('password') or not data.get('full_name'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user = User(
            email=data['email'],
            full_name=data['full_name'],
            role=data.get('role', 'executive')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user registered: {user.email}")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# -----------------------------
# User Login (Email/Password)
# -----------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint
    
    Request body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing email or password'}), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is inactive'}), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Store user in session
        session['user_id'] = user.id
        session['user_email'] = user.email
        
        logger.info(f"User logged in: {user.email}")
        
        return jsonify({
            'message': 'Login successful',
            'token': f'session_{user.id}',  # Simple token for demo
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# -----------------------------
# Get Current User
# -----------------------------
@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Get current authenticated user
    """
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
    
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# -----------------------------
# Google OAuth - Get URL
# -----------------------------
@auth_bp.route('/google/url', methods=['GET'])
def google_auth_url():
    """
    Get Google OAuth authorization URL
    """
    try:
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/api/auth/google/callback')
        
        if not client_id:
            return jsonify({'error': 'Google OAuth not configured'}), 500
        
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope=openid email profile "
            f"https://www.googleapis.com/auth/gmail.readonly "
            f"https://www.googleapis.com/auth/calendar&"
            f"access_type=offline&"
            f"prompt=consent"
        )
        
        return jsonify({'url': auth_url}), 200
    
    except Exception as e:
        logger.error(f"Google OAuth URL error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# -----------------------------
# Google OAuth - Callback
# -----------------------------
@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    """
    Handle Google OAuth callback
    """
    try:
        code = request.args.get('code')
        
        if not code:
            return redirect('http://localhost:5000/frontend/login.html?error=no_code')
        
        # For now, just redirect to dashboard
        # In full implementation, exchange code for tokens
        
        return redirect('http://localhost:5000/frontend/index.html?google_auth=success')
    
    except Exception as e:
        logger.error(f"Google OAuth callback error: {str(e)}")
        return redirect('http://localhost:5000/frontend/login.html?error=oauth_failed')


# -----------------------------
# Logout
# -----------------------------
@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout user
    """
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200