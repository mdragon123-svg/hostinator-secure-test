"""
Marketplace application data and configuration
"""
from collections import OrderedDict

# Original marketplace apps
_MARKETPLACE_APPS = {
    'Docker': {
        'category': 'DeveloperTools',
        'description': 'Container platform for building and running applications in isolated environments.',
        'image': 'https://cdn.iconscout.com/icon/free/png-256/docker-226091.png',
        'deployment_type': None
    },
    'WordPress': {
        'category': 'Hosting',
        'description': 'Launch a blog or website with the most popular CMS in the world.',
        'image': 'https://cdn-icons-png.flaticon.com/512/174/174881.png',
        'deployment_type': 'WordPress'
    },
    'Laravel': {
        'category': 'Framework',
        'description': 'Rapidly build web apps using elegant and modern PHP framework.',
        'image': 'https://laravel.com/img/logomark.min.svg',
        'deployment_type': None
    },
    'cPanel': {
        'category': 'DeveloperTools',
        'description': 'Host and manage websites, databases, emails with ease using cPanel.',
        'image': 'https://images.seeklogo.com/logo-png/27/1/cpanel-logo-png_seeklogo-273009.png',
        'deployment_type': None
    },
    'Moodle': {
        'category': 'DeveloperTools',
        'description': 'Create online learning platforms with Moodle LMS, enhance the way you learn.',
        'image': 'https://miro.medium.com/v2/resize:fit:1400/1*zdEOGj6ZF3eKbgDO1EsdSA.jpeg',
        'deployment_type': 'Moodle'
    },
    'Zabbix': {
        'category': 'Monitoring',
        'description': 'Monitor your infrastructure and apps with the powerful Zabbix platform.',
        'image': 'https://assets.zabbix.com/img/logo/zabbix_logo_500x131.png',
        'deployment_type': 'Zabbix'
    },
    'Nextcloud': {
        'category': 'Hosting',
        'description': 'Private cloud storage solution for file sync and collaboration.',
        'image': 'https://upload.wikimedia.org/wikipedia/commons/6/60/Nextcloud_Logo.svg',
        'deployment_type': 'NextCloud'
    },
    'Django': {
        'category': 'Framework',
        'description': 'High-level Python web framework that encourages rapid development and clean design.',
        'image': 'https://static.djangoproject.com/img/logos/django-logo-negative.svg',
        'deployment_type': None
    },
    'LAMP': {
        'category': 'Stack',
        'description': 'Linux, Apache, MySQL, PHP stack for web app hosting and development.',
        'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRIB8tCNLMXC-MuS67HzCf0dv_0VA1LOMvC-g&s',
        'deployment_type': None
    },
    'LEMP': {
        'category': 'Stack',
        'description': 'Linux, Nginx, MySQL, PHP stack. High-performance alternative to LAMP.',
        'image': 'https://www.accuwebhosting.com/blog/wp-content/uploads/2024/01/1___YhA5RwN4yWeabV8M1YlA-2.png',
        'deployment_type': None
    },
    'MERN': {
        'category': 'Stack',
        'description': 'MongoDB, Express, React, Node.js — modern JS stack for full-stack apps.',
        'image': 'https://upload.wikimedia.org/wikipedia/commons/d/d9/Node.js_logo.svg',
        'deployment_type': None
    },
    'Plesk': {
        'category': 'DeveloperTools',
        'description': 'All-in-one web hosting platform to manage websites, mail, and more.',
        'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSEB4HKNCy7jiaeBS0hRnhl7YEg5KLiOYmQFw&s',
        'deployment_type': None
    },
    'Postiz': {
        'category': 'DeveloperTools',
        'description': 'Social media management, analytics and scheduling platform.',
        'image': 'https://postiz.com/favicon.ico',
        'deployment_type': None
    },
    'Joomla': {
        'category': 'Hosting',
        'description': 'Powerful content management system for building websites.',
        'image': 'https://upload.wikimedia.org/wikipedia/commons/e/e8/Joomla%21-Logo.svg',
        'deployment_type': 'Joomla'
    },
    'Ghost': {
        'category': 'Hosting',
        'description': 'Modern publishing platform for creating blogs and publications.',
        'image': 'https://ghost.org/images/logos/ghost-logo-dark.png',
        'deployment_type': 'Ghost'
    },
    'Metabase': {
        'category': 'DeveloperTools',
        'description': 'Business intelligence and analytics platform.',
        'image': 'https://www.metabase.com/images/logo.svg',
        'deployment_type': 'Metabase'
    },
    'Jupyter Notebook': {
        'category': 'DeveloperTools',
        'description': 'Python Coding and Development IDE.',
        'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/883px-Jupyter_logo.svg.png',
        'deployment_type': 'Jupyter'
    }
}

# Reorder: supported apps first, unsupported apps later
MARKETPLACE_APPS = OrderedDict()

# Supported (deployment_type is NOT None)
for name, app in _MARKETPLACE_APPS.items():
    if app['deployment_type'] is not None:
        MARKETPLACE_APPS[name] = app

# Unsupported (deployment_type is None)
for name, app in _MARKETPLACE_APPS.items():
    if app['deployment_type'] is None:
        MARKETPLACE_APPS[name] = app
