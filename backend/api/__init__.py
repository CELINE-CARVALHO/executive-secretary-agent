from backend.api.auth import auth_bp
from backend.api.emails import emails_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(emails_bp, url_prefix="/api/emails")
