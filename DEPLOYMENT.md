# Deployment Guide

This guide provides instructions for deploying the Crypto Trading Data Processor application in different environments.

## 🚀 Local Development

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd AccountWebDev

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The application will be available at `http://localhost:3000`

## 🌐 Production Deployment

### Option 1: Using Gunicorn (Recommended)

1. **Install Gunicorn:**
```bash
pip install gunicorn
```

2. **Create a WSGI entry point:**
Create a file named `wsgi.py` in the root directory:
```python
from app import app

if __name__ == "__main__":
    app.run()
```

3. **Run with Gunicorn:**
```bash
gunicorn --bind 0.0.0.0:8000 wsgi:app
```

### Option 2: Using uWSGI

1. **Install uWSGI:**
```bash
pip install uwsgi
```

2. **Create uWSGI configuration file (`uwsgi.ini`):**
```ini
[uwsgi]
module = wsgi:app
master = true
processes = 4
socket = /tmp/uwsgi.sock
chmod-socket = 660
vacuum = true
die-on-term = true
```

3. **Run with uWSGI:**
```bash
uwsgi --ini uwsgi.ini
```

### Option 3: Using Docker

1. **Create Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["python", "app.py"]
```

2. **Build and run:**
```bash
docker build -t crypto-trading-processor .
docker run -p 3000:3000 crypto-trading-processor
```

## 🔧 Environment Configuration

### Environment Variables
Create a `.env` file for configuration:
```env
FLASK_ENV=production
FLASK_DEBUG=False
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

### Security Considerations
- Use HTTPS in production
- Set up proper firewall rules
- Implement rate limiting
- Use environment variables for sensitive configuration
- Regular security updates

## 📊 Monitoring and Logging

### Application Logs
The application logs errors and processing information. Consider using:
- **Logging**: Configure Python logging
- **Monitoring**: Use tools like Prometheus/Grafana
- **Error Tracking**: Services like Sentry

### Health Checks
Implement health check endpoints:
```python
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})
```

## 🔄 Updates and Maintenance

### Updating the Application
1. Pull latest changes: `git pull origin main`
2. Install updated dependencies: `pip install -r requirements.txt`
3. Restart the application

### Backup Strategy
- Regular backups of uploaded files
- Database backups (if using database)
- Configuration backups

## 🛠️ Troubleshooting

### Common Issues

1. **Port already in use:**
```bash
# Find process using port 3000
netstat -tulpn | grep :3000
# Kill the process
kill -9 <PID>
```

2. **Permission denied:**
```bash
# Ensure uploads directory exists and is writable
mkdir -p uploads
chmod 755 uploads
```

3. **Memory issues:**
- Monitor memory usage
- Consider increasing server resources
- Implement file size limits

### Performance Optimization
- Use CDN for static files
- Implement caching
- Optimize database queries (if applicable)
- Use load balancers for high traffic

## 📞 Support

For deployment issues:
1. Check application logs
2. Verify environment configuration
3. Test with sample data
4. Contact support team 