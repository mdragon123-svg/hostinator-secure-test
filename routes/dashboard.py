"""
Dashboard routes
"""
from flask import Blueprint, render_template, redirect, url_for, session, flash
import logging
from database import db_manager
from utils import str_to_datetime
from datetime import datetime

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

def login_required(f):
    """Decorator to require login"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@dashboard_bp.route('/')
@login_required
def index():
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    
    try:
        deployments_raw = db_manager.execute_query("SELECT * FROM deployments WHERE user_id = %s ORDER BY created_at DESC", (user_id,), fetch=True)
        
        deployments = []
        for d in deployments_raw:
            deployment = dict(d)
            try:
                deployment['created_at'] = str_to_datetime(deployment['created_at'])
                deployment['last_updated'] = str_to_datetime(deployment['last_updated'])
            except Exception as e:
                logger.error(f"Error converting date: {e}")
                deployment['created_at'] = datetime.now()
                deployment['last_updated'] = datetime.now()
            deployments.append(deployment)
        
        total_deployments = len(deployments)
        active_deployments = sum(1 for d in deployments if d['status'] == 'Active')
        inactive_deployments = sum(1 for d in deployments if d['status'] == 'Inactive')
        pending_deployments = sum(1 for d in deployments if d['status'] == 'Pending')
        
        deployment_types = {}
        for d in deployments:
            if d['deployment_type'] in deployment_types:
                deployment_types[d['deployment_type']] += 1
            else:
                deployment_types[d['deployment_type']] = 1
        
        return render_template('dashboard.html', 
                              deployments=deployments,
                              total_deployments=total_deployments,
                              active_deployments=active_deployments,
                              inactive_deployments=inactive_deployments,
                              pending_deployments=pending_deployments,
                              deployment_types=deployment_types)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        flash('Error loading dashboard. Please try again.', 'error')
        return render_template('dashboard.html', 
                              deployments=[],
                              total_deployments=0,
                              active_deployments=0,
                              inactive_deployments=0,
                              pending_deployments=0,
                              deployment_types={})
