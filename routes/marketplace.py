"""
Marketplace routes
"""
from flask import Blueprint, render_template, redirect, url_for, session, flash
from marketplace_data import MARKETPLACE_APPS

marketplace_bp = Blueprint('marketplace', __name__)

def login_required(f):
    """Decorator to require login"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@marketplace_bp.route('/marketplace')
@login_required
def marketplace():
    """Marketplace main page - requires authentication"""
    return render_template('marketplace.html', apps=MARKETPLACE_APPS)

@marketplace_bp.route('/marketplace/deploy/<app_name>')
@login_required
def marketplace_deploy(app_name):
    """Deploy an app from marketplace - redirect to new deployment with pre-selected type"""
    if app_name not in MARKETPLACE_APPS:
        flash('Application not found', 'error')
        return redirect(url_for('marketplace.marketplace'))
    
    app_info = MARKETPLACE_APPS[app_name]
    
    # Check if the app is supported by hostinator
    if not app_info['deployment_type']:
        flash(f'{app_name} deployment is coming soon! Not yet supported.', 'info')
        return redirect(url_for('marketplace.marketplace'))
    
    # Redirect to new deployment with pre-selected type
    return redirect(url_for('deployments.new_deployment', 
                           app_name=app_name, 
                           deployment_type=app_info['deployment_type']))
