# WSGI Entry Point for Production (Gunicorn)

from app import create_app

app = create_app('production')
