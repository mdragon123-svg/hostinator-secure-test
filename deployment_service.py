"""
Deployment management service
"""
import logging
from datetime import datetime
from ssh_manager import SSHManager
from config import Config

logger = logging.getLogger(__name__)

class DeploymentService:
    """Service for managing deployments"""
    
    def __init__(self):
        self.ssh_manager = SSHManager(Config.SSH_CONFIG)
        # Updated script paths to use setup_service directory
        self.script_mapping = {
            'WordPress': 'setup_wp.sh',
            'NextCloud': 'setup_nc.sh',
            'Moodle': 'setup_moodle.sh',
            'Zabbix': 'setup_zabbix.sh',
            #'Postiz': 'setup_postiz/setup_postiz.sh',
            'Joomla': 'setup_joomla.sh',
            'Ghost': 'setup_ghost.sh',
            'Metabase': 'setup_metabase.sh',
            'Jupyter': 'setup_jupyter.sh'          
        }
        
        self.delete_script_mapping = {
            'WordPress': 'delete_wp.sh',
            'NextCloud': 'delete_nc.sh',
            'Moodle': 'delete_moodle.sh',
            'Zabbix': 'delete_zabbix.sh',
           # 'Postiz': 'delete_postiz.sh',
            'Joomla': 'delete_joomla.sh',
            'Ghost': 'delete_ghost.sh',
            'Metabase': 'delete_metabase.sh',
            'Jupyter': 'delete_jupyter.sh'
        }
    
    def execute_deployment_script(self, domain, email, deployment_type):
        """Execute deployment script for given parameters"""
        try:
            if deployment_type not in self.script_mapping:
                return {
                    'success': False,
                    'output': "Deployment type not supported",
                    'credentials_file': None
                }
            
            script_name = self.script_mapping[deployment_type]
            command = f"cd ~ && ./{script_name} {domain} {email}"
            result = self.ssh_manager.execute_command(command)
            
            if result['success']:
                credentials_file = f"/home/{domain}/credentials_{domain}.txt"
                
                return {
                    'success': True,
                    'output': result['output'],
                    'credentials_file': credentials_file
                }
            else:
                return {
                    'success': False,
                    'output': result['output'],
                    'credentials_file': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'output': f"Error: {str(e)}",
                'credentials_file': None
            }
    
    def execute_container_action(self, domain, action, deployment_type):
        """Execute container actions with proper timeout handling for delete operations"""
        try:
            if action == 'stop':
                return self._stop_container(domain)
            elif action == 'start':
                return self._start_container(domain)
            elif action == 'delete':
                return self._delete_container(domain, deployment_type)
            else:
                return {
                    'success': False,
                    'output': f"Action {action} not supported"
                }
        except Exception as e:
            return {
                'success': False,
                'output': f"Error: {str(e)}"
            }
    
    def _stop_container(self, domain):
        """Stop container for domain"""
        check_command = f"test -f /home/{domain}/docker-compose.yml && echo 'exists' || echo 'not found'"
        check_result = self.ssh_manager.execute_command(check_command)
        
        if 'not found' in check_result.get('output', ''):
            return {
                'success': False,
                'output': f"docker-compose.yml not found for {domain}"
            }
        
        command = f"cd /home/{domain} && docker-compose stop"
        result = self.ssh_manager.execute_command(command)
        
        return {
            'success': result['success'],
            'output': result['output']
        }
    
    def _start_container(self, domain):
        """Start container for domain"""
        check_command = f"test -f /home/{domain}/docker-compose.yml && echo 'exists' || echo 'not found'"
        check_result = self.ssh_manager.execute_command(check_command)
        
        if 'not found' in check_result.get('output', ''):
            return {
                'success': False,
                'output': f"docker-compose.yml not found for {domain}"
            }
        
        command = f"cd /home/{domain} && docker-compose start"
        result = self.ssh_manager.execute_command(command)
        
        return {
            'success': result['success'],
            'output': result['output']
        }
    
    def _delete_container(self, domain, deployment_type):
        """Delete container and cleanup"""
        if deployment_type not in self.delete_script_mapping:
            return {
                'success': False,
                'output': "Deployment type not supported for deletion"
            }
        
        script_name = self.delete_script_mapping[deployment_type]
        
        # Check if script exists with shorter timeout (10 seconds)
        check_command = f"test -f ~/{script_name} && echo 'exists' || echo 'not found'"
        check_result = self.ssh_manager.execute_command(check_command, timeout=10)
        
        if 'not found' in check_result.get('output', ''):
            return {
                'success': False,
                'output': f"Delete script {script_name} not found on backend server"
            }
        
        # Execute delete script with force kill if stuck (60 second limit + cleanup)
        command = f"timeout 60 bash -c 'cd ~ && ./{script_name} {domain}' || (echo 'Delete operation timed out but continuing cleanup' && pkill -f '{script_name}' 2>/dev/null; rm -rf /home/{domain} 2>/dev/null; echo 'Forced cleanup completed')"
        result = self.ssh_manager.execute_command(command, timeout=90)
        
        return {
            'success': result['success'],
            'output': result['output']
        }
    
    def read_credentials_file(self, file_path):
        """Read credentials file from remote server"""
        return self.ssh_manager.read_remote_file(file_path)
