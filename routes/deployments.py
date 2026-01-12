"""
Deployment management routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import logging
from datetime import datetime
from database import db_manager
from deployment_service import DeploymentService
from utils import str_to_datetime
import traceback
import re  # [SECURITY] Import re for validation

logger = logging.getLogger(__name__)

deployments_bp = Blueprint('deployments', __name__)
deployment_service = DeploymentService()

# [SECURITY] Strong Regex for Domain Validation
# Allows: alphanumeric, hyphens, dots. No spaces, no special chars like ; | & $
DOMAIN_REGEX = re.compile(r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$')

def login_required(f):
    """Decorator to require login"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@deployments_bp.route('/deployment/<int:id>')
@login_required
def deployment_detail(id):
    user_id = session['user_id']
    
    try:
        deployment_raw = db_manager.execute_query("SELECT * FROM deployments WHERE id = %s AND user_id = %s", (id, user_id), fetch_one=True)
        
        if deployment_raw:
            deployment = dict(deployment_raw)
            try:
                deployment['created_at'] = str_to_datetime(deployment['created_at'])
                deployment['last_updated'] = str_to_datetime(deployment['last_updated'])
            except Exception as e:
                logger.error("Error converting date: %s", e)
                deployment['created_at'] = datetime.now()
                deployment['last_updated'] = datetime.now()
            
            credentials_content = None
            if deployment['credentials_file']:
                credentials_content = deployment_service.read_credentials_file(deployment['credentials_file'])
            
            return render_template('deployment.html', 
                                  deployment=deployment, 
                                  credentials_content=credentials_content)
        else:
            flash('Deployment not found or you do not have permission to view it', 'error')
            return redirect(url_for('dashboard.dashboard'))
    except Exception as e:
        logger.error("Deployment detail error: %s", e)
        flash('Error loading deployment details. Please try again.', 'error')
        return redirect(url_for('dashboard.dashboard'))

@deployments_bp.route('/deployment/new', methods=['GET', 'POST'])
@login_required
def new_deployment():
    # Check if this came from marketplace
    app_name = request.args.get('app_name', '')
    pre_selected_type = request.args.get('deployment_type', '')
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        deployment_type = request.form['deployment_type']
        
        # [SECURITY] Validate Domain Name format
        if not DOMAIN_REGEX.match(name):
            flash('Invalid domain name format. Only letters, numbers, dashes, and dots allowed.', 'error')
            return render_template('new_deployment.html', 
                                  app_name=app_name, 
                                  pre_selected_type=pre_selected_type)

        now = datetime.now()
        user_id = session['user_id']
        
        try:
            # FIXED: Changed initial status from 'Deploying' to 'Pending'
            deployment_id = db_manager.execute_query('''
            INSERT INTO deployments (name, email, status, deployment_type, created_at, last_updated, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (name, email, 'Pending', deployment_type, now, now, user_id))
            
            flash(f'Deployment started for {app_name if app_name else deployment_type}. Please wait while we set up your environment.', 'info')
            return redirect(url_for('deployments.deployment_progress', id=deployment_id))
        except Exception as e:
            logger.error("New deployment error: %s", e)
            flash('Error creating deployment. Please try again.', 'error')
    
    return render_template('new_deployment.html', 
                          app_name=app_name, 
                          pre_selected_type=pre_selected_type)

@deployments_bp.route('/deployment/progress/<int:id>')
@login_required
def deployment_progress(id):
    user_id = session['user_id']
    
    try:
        deployment = db_manager.execute_query("SELECT * FROM deployments WHERE id = %s AND user_id = %s", (id, user_id), fetch_one=True)
        
        if not deployment:
            flash('Deployment not found or you do not have permission to view it', 'error')
            return redirect(url_for('dashboard.dashboard'))
        
        return render_template('deployment_progress.html', deployment=deployment)
    except Exception as e:
        logger.error("Deployment progress error: %s", e)
        flash('Error loading deployment progress. Please try again.', 'error')
        return redirect(url_for('dashboard.dashboard'))

@deployments_bp.route('/api/execute-deployment/<int:id>', methods=['POST'])
@login_required
def execute_deployment_api(id):
    """Execute deployment script - this runs in background"""
    user_id = session['user_id']
    
    try:
        # Set content type to JSON
        response_headers = {'Content-Type': 'application/json'}
        
        deployment = db_manager.execute_query("SELECT * FROM deployments WHERE id = %s AND user_id = %s", (id, user_id), fetch_one=True)
        
        if not deployment:
            logger.warning("Deployment %s not found for user %s", id, user_id)
            return jsonify({
                'success': False, 
                'error': 'Deployment not found or access denied', 
                'output': 'Deployment not found or you do not have permission to access it.'
            }), 404, response_headers
        
        name = deployment['name']
        email = deployment['email']
        deployment_type = deployment['deployment_type']
        
        # [SECURITY] Double-check domain validation even here (Defense in Depth)
        if not DOMAIN_REGEX.match(name):
             return jsonify({
                'success': False, 
                'error': 'Invalid domain format detected', 
                'output': 'Security validation failed for domain name.'
            }), 400, response_headers

        logger.info("🚀 Starting deployment for deployment ID %s, Type: %s, User: %s", id, deployment_type, user_id)
        
        # FIXED: Update status to 'Pending' first to ensure it's counted correctly
        # Then update to 'Deploying' to show it's in progress
        now = datetime.now()
        db_manager.execute_query('''
        UPDATE deployments 
        SET status = %s, last_updated = %s 
        WHERE id = %s
        ''', ('Pending', now, id))
        
        # Execute the deployment script
        result = deployment_service.execute_deployment_script(name, email, deployment_type)
        
        if result['success']:
            # Update to Active status
            now = datetime.now()
            db_manager.execute_query('''
            UPDATE deployments 
            SET status = %s, last_updated = %s, credentials_file = %s 
            WHERE id = %s
            ''', ('Active', now, result['credentials_file'], id))
            
            logger.info("✅ Deployment %s completed successfully", id)
            return jsonify({
                'success': True,
                'message': 'Deployment completed successfully',
                'output': result['output'],
                'status': 'Active'
            }), 200, response_headers
        else:
            # Update to Failed/Inactive status
            now = datetime.now()
            db_manager.execute_query('''
            UPDATE deployments 
            SET status = %s, last_updated = %s 
            WHERE id = %s
            ''', ('Inactive', now, id))
            
            logger.error("❌ Deployment %s failed: %s", id, result['output'])
            return jsonify({
                'success': False,
                'message': 'Deployment failed',
                'output': result['output'],
                'status': 'Failed'
            }), 200, response_headers  # Still return 200 to ensure JSON parsing works
            
    except Exception as e:
        logger.error("💥 Execute deployment API error for ID %s: %s", id, e)
        logger.error("Traceback: %s", traceback.format_exc())
        
        # Ensure we update the database even on exception
        try:
            now = datetime.now()
            db_manager.execute_query('''
            UPDATE deployments 
            SET status = %s, last_updated = %s 
            WHERE id = %s
            ''', ('Inactive', now, id))
        except:
            pass  # Don't let database update failure mask the original error
        
        return jsonify({
            'success': False, 
            'error': 'Internal server error',
            'output': f'Server error occurred: {str(e)}',
            'status': 'Failed'
        }), 200, {'Content-Type': 'application/json'}  # Always return JSON

@deployments_bp.route('/api/deployment-status/<int:id>', methods=['GET'])
@login_required
def get_deployment_status(id):
    """Get current deployment status - for polling"""
    user_id = session['user_id']
    
    try:
        deployment = db_manager.execute_query(
            "SELECT status, last_updated FROM deployments WHERE id = %s AND user_id = %s", 
            (id, user_id), 
            fetch_one=True
        )
        
        if not deployment:
            return jsonify({'error': 'Deployment not found'}), 404
        
        return jsonify({
            'status': deployment['status'],
            'last_updated': deployment['last_updated'].isoformat() if deployment['last_updated'] else None
        }), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        logger.error("Get deployment status error: %s", e)
        return jsonify({'error': 'Internal server error'}), 500

@deployments_bp.route('/deployment/delete/<int:id>', methods=['POST'])
@login_required
def delete_deployment(id):
    """Delete deployment with improved error handling and guaranteed database cleanup"""
    user_id = session['user_id']
    
    try:
        deployment = db_manager.execute_query("SELECT name, deployment_type FROM deployments WHERE id = %s AND user_id = %s", (id, user_id), fetch_one=True)
        
        if deployment:
            domain = deployment['name']
            deployment_type = deployment['deployment_type']
            
            # Add immediate feedback to prevent browser hang perception
            flash('Delete operation started. This may take a moment...', 'info')
            
            try:
                result = deployment_service.execute_container_action(domain, 'delete', deployment_type)
                
                if result['success']:
                    db_manager.execute_query("DELETE FROM deployments WHERE id = %s", (id,))
                    flash('Deployment deleted successfully!', 'success')
                else:
                    # Even if delete script fails, remove from database to prevent UI issues
                    db_manager.execute_query("DELETE FROM deployments WHERE id = %s", (id,))
                    flash(f'Deployment removed from dashboard. Note: {result["output"]}', 'warning')
            except Exception as e:
                # Fallback - remove from database even if there's an error
                db_manager.execute_query("DELETE FROM deployments WHERE id = %s", (id,))
                flash(f'Deployment removed from dashboard. Error during cleanup: {str(e)}', 'warning')
        else:
            flash('Deployment not found or you do not have permission to delete it', 'error')
    except Exception as e:
        logger.error("Delete deployment error: %s", e)
        flash('Error deleting deployment. Please try again.', 'error')
    
    return redirect(url_for('dashboard.dashboard'))

@deployments_bp.route('/deployment/update-status/<int:id>', methods=['POST'])
@login_required
def update_deployment_status(id):
    user_id = session['user_id']
    
    status = request.form.get('status')
    action = request.form.get('action', '')
    
    if not status or status not in ['Active', 'Inactive', 'Pending']:
        flash('Invalid status', 'error')
        return redirect(url_for('deployments.deployment_detail', id=id))
    
    try:
        deployment = db_manager.execute_query("SELECT name, deployment_type FROM deployments WHERE id = %s AND user_id = %s", (id, user_id), fetch_one=True)
        
        if deployment:
            domain = deployment['name']
            deployment_type = deployment['deployment_type']
            
            if action == 'stop' and status == 'Inactive':
                result = deployment_service.execute_container_action(domain, 'stop', deployment_type)
                if not result['success']:
                    flash(f'Error stopping container: {result["output"]}', 'error')
                    return redirect(url_for('deployments.deployment_detail', id=id))
            elif action == 'start' and status == 'Active':
                result = deployment_service.execute_container_action(domain, 'start', deployment_type)
                if not result['success']:
                    flash(f'Error starting container: {result["output"]}', 'error')
                    return redirect(url_for('deployments.deployment_detail', id=id))
            
            now = datetime.now()
            db_manager.execute_query("UPDATE deployments SET status = %s, last_updated = %s WHERE id = %s", 
                         (status, now, id))
            
            flash(f'Deployment status updated to {status}', 'success')
        else:
            flash('Deployment not found or you do not have permission to update it', 'error')
    except Exception as e:
        logger.error("Update deployment status error: %s", e)
        flash('Error updating deployment status. Please try again.', 'error')
    
    return redirect(url_for('deployments.deployment_detail', id=id))

@deployments_bp.route('/deployment/credentials/<int:id>')
@login_required
def get_deployment_credentials(id):
    user_id = session['user_id']
    
    try:
        deployment = db_manager.execute_query("SELECT credentials_file FROM deployments WHERE id = %s AND user_id = %s", (id, user_id), fetch_one=True)
        
        if not deployment or not deployment['credentials_file']:
            return jsonify({'error': 'No credentials file found or you do not have permission'}), 404
        
        credentials_content = deployment_service.read_credentials_file(deployment['credentials_file'])
        if not credentials_content:
            return jsonify({'error': 'Could not read credentials file'}), 500
        
        return jsonify({'credentials': credentials_content})
    except Exception as e:
        logger.error("Get credentials error: %s", e)
        return jsonify({'error': 'Internal server error'}), 500
