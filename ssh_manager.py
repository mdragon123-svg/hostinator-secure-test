"""
SSH connection and remote server management
"""
import paramiko
import logging

logger = logging.getLogger(__name__)

class SSHManager:
    """SSH connection and remote command execution"""
    
    def __init__(self, ssh_config):
        self.ssh_config = ssh_config
    
    def create_ssh_client(self):
        """Create and return an SSH client connection"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect(
                hostname=self.ssh_config['hostname'],
                port=self.ssh_config['port'],
                username=self.ssh_config['username'],
                password=self.ssh_config['password']
            )
            return ssh
        except Exception as e:
            logger.error(f"Failed to connect to SSH: {e}")
            raise
    
    def execute_command(self, command, timeout=300):
        """Execute a command on the remote server via SSH with configurable timeout"""
        try:
            ssh = self.create_ssh_client()
            stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            exit_status = stdout.channel.recv_exit_status()
            ssh.close()
            
            if exit_status != 0 and error:
                return {'success': False, 'output': error}
            
            return {'success': True, 'output': output if output else "Command executed successfully"}
        except Exception as e:
            return {'success': False, 'output': f"SSH Error: {str(e)}"}
    
    def read_remote_file(self, file_path):
        """Read a file from the remote server via SSH"""
        if not file_path:
            return None
        
        try:
            ssh = self.create_ssh_client()
            sftp = ssh.open_sftp()
            
            with sftp.open(file_path, 'r') as file:
                content = file.read().decode('utf-8')
            
            sftp.close()
            ssh.close()
            
            return content
        except Exception as e:
            logger.error(f"Error reading remote file: {e}")
            return None
