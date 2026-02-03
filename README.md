# Medium-Style Blog Platform

A beautiful, fully-featured blog platform inspired by Medium. Built with Flask.

## Features

- ✅ **Admin-Only Posting** - Secure login for content management
- ✅ **Public Reading** - Beautiful reading experience for visitors
- ✅ **Rich Text Editor** - TinyMCE WYSIWYG editor
- ✅ **Dark Mode** - Toggle between light and dark themes
- ✅ **SEO Optimized** - Meta tags and Open Graph support
- ✅ **Reading Time** - Automatic calculation
- ✅ **Tags** - Categorize and filter posts
- ✅ **Search** - Full-text search across posts
- ✅ **Responsive** - Works on all devices
- ✅ **Deploy Ready** - Docker and Gunicorn support

## Quick Start

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run the application
python run.py
```

Visit http://localhost:5000

### Default Admin Credentials

- **Username:** admin
- **Password:** admin123

> ⚠️ **Important:** Change the password immediately after first login!

## Deployment

### Docker Compose (Recommended)

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f
```

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set production environment
export FLASK_CONFIG=production
export SECRET_KEY=your-secure-secret-key
export DATABASE_URL=postgresql://user:pass@host:5432/db

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app
```

## Hosting Options

This app is ready to deploy on:

- **Railway** - Connect GitHub repo, auto-detects Dockerfile
- **Render** - Free tier available, use Gunicorn start command
- **Fly.io** - Use `fly launch` to detect Dockerfile
- **DigitalOcean App Platform** - Supports Docker deployment
- **Heroku** - Add `Procfile` with: `web: gunicorn wsgi:app`

## Configuration

Edit `.env` file or set environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | Required |
| `DATABASE_URL` | PostgreSQL connection URL | SQLite (dev) |
| `BLOG_TITLE` | Blog title | My Blog |
| `BLOG_SUBTITLE` | Blog tagline | Thoughts, stories... |
| `BLOG_AUTHOR` | Author name | Admin |

## Project Structure

```
Blog/
├── app/
│   ├── auth/           # Authentication blueprint
│   ├── blog/           # Blog blueprint
│   ├── static/
│   │   ├── css/        # Stylesheets
│   │   └── uploads/    # Uploaded images
│   ├── templates/      # Jinja2 templates
│   ├── __init__.py     # App factory
│   └── models.py       # Database models
├── config.py           # Configuration
├── run.py              # Development entry point
├── wsgi.py             # Production entry point
├── requirements.txt    # Dependencies
├── Dockerfile          # Docker configuration
└── docker-compose.yml  # Docker Compose config
```

## License

MIT License
