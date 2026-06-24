# RapidRepair Node.js Integration Guide

This document describes how to use RapidRepair with the new Node.js Worker service for enhanced booking management, analytics, and notifications.

## Architecture Overview

RapidRepair now runs as a **multi-service application**:

```
┌─────────────────────────────────────────────────────────┐
│                 RapidRepair Services                     │
├──────────────────────┬──────────────────────────────────┤
│                      │                                  │
│  Flask Backend       │      Node.js Worker             │
│  Port: 5000          │      Port: 3000                 │
│                      │                                  │
│  • Web UI            │  • Booking Analytics            │
│  • Booking Form      │  • Status Management            │
│  • Quote Estimator   │  • Notifications               │
│  • Admin Panel       │  • Background Jobs              │
│                      │                                  │
└──────────────────────┴──────────────────────────────────┘
           │                         │
           └─────────────────────────┘
                      │
              ┌───────▼────────┐
              │ SQLite Database│
              │  rapidrepair.db│
              └────────────────┘
```

## Quick Start

### Option 1: Automated (Recommended)

**Linux/macOS:**
```bash
chmod +x run-services.sh
./run-services.sh
```

**Windows PowerShell:**
```powershell
.\run-services.ps1
```

This will automatically:
1. Start the Flask app (port 5000)
2. Install Node.js dependencies
3. Start the Worker service (port 3000)
4. Display service URLs and health checks

### Option 2: Manual

**Terminal 1 - Flask App:**
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
python app.py
```

**Terminal 2 - Node.js Worker:**
```bash
cd worker
npm install
npm start
```

## Service Endpoints

### Flask App (http://127.0.0.1:5000)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Homepage with service catalog |
| `/book` | POST | Create new booking |
| `/booking/<id>` | GET | Booking confirmation page |
| `/admin/bookings` | GET | Admin dashboard with all bookings |
| `/api/services` | GET | Get all services (JSON) |
| `/api/estimate` | POST | Get quote estimate (JSON) |

### Worker Service (http://127.0.0.1:3000)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/worker/health` | GET | Health check |
| `/api/worker/bookings` | GET | List all bookings with optional status filter |
| `/api/worker/analytics` | GET | Get comprehensive booking statistics |
| `/api/worker/bookings/<id>/status` | POST | Update booking status |
| `/api/worker/bookings/<id>/notify` | POST | Queue notification for booking |

## Usage Examples

### 1. Get Analytics Data

Fetch real-time analytics about all bookings:

```bash
curl http://localhost:3000/api/worker/analytics
```

**Response:**
```json
{
  "success": true,
  "analytics": {
    "totalBookings": 25,
    "totalRevenue": 12450,
    "averageQuote": 498,
    "averageServiceTime": 52,
    "bookingsByStatus": [
      { "status": "New", "count": 8 },
      { "status": "Completed", "count": 15 },
      { "status": "Cancelled", "count": 2 }
    ],
    "bookingsByService": [
      { "name": "AC General Service", "count": 12 },
      { "name": "AC Repair Visit", "count": 6 },
      { "name": "Gas Refill", "count": 4 }
    ]
  },
  "timestamp": "2024-06-24T07:07:00.000Z"
}
```

### 2. Update Booking Status

Mark a booking as confirmed:

```bash
curl -X POST http://localhost:3000/api/worker/bookings/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "Confirmed"}'
```

**Valid statuses:**
- `New` - Initial state when booking is created
- `Confirmed` - Admin has confirmed the booking
- `In Progress` - Technician is on the way
- `Completed` - Service has been completed
- `Cancelled` - Booking was cancelled

### 3. Filter Bookings by Status

Get only new bookings:

```bash
curl "http://localhost:3000/api/worker/bookings?status=New"
```

### 4. Queue Notification

Send notification for a booking:

```bash
curl -X POST http://localhost:3000/api/worker/bookings/1/notify \
  -H "Content-Type: application/json" \
  -d '{"method": "sms"}'
```

**Supported methods:**
- `email` - Email notification
- `sms` - SMS notification
- `whatsapp` - WhatsApp notification
- Omit for all available channels

## Integration with Admin Dashboard

You can integrate the Worker APIs with your Flask admin dashboard:

### Python Example (Using Requests)

```python
import requests

# Get analytics data
response = requests.get('http://localhost:3000/api/worker/analytics')
analytics = response.json()

print(f"Total Bookings: {analytics['analytics']['totalBookings']}")
print(f"Total Revenue: ₹{analytics['analytics']['totalRevenue']}")

# Update booking status
status_response = requests.post(
    'http://localhost:3000/api/worker/bookings/1/status',
    json={'status': 'Confirmed'}
)

# Send notification
notify_response = requests.post(
    'http://localhost:3000/api/worker/bookings/1/notify',
    json={'method': 'sms'}
)
```

### JavaScript Example

```javascript
// Get analytics
const analyticsResponse = await fetch('http://localhost:3000/api/worker/analytics');
const analytics = await analyticsResponse.json();
console.log(`Total Revenue: ₹${analytics.analytics.totalRevenue}`);

// Update status
const statusResponse = await fetch('http://localhost:3000/api/worker/bookings/1/status', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ status: 'Confirmed' })
});

// Send notification
const notifyResponse = await fetch('http://localhost:3000/api/worker/bookings/1/notify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ method: 'sms' })
});
```

## Configuration

### Environment Variables

Edit `worker/.env`:

```
# Server Configuration
WORKER_PORT=3000
FLASK_API_URL=http://127.0.0.1:5000
DATABASE_PATH=../rapidrepair.db

# Notification Settings (for future use)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Feature Flags
ENABLE_EMAIL_NOTIFICATIONS=false
ENABLE_ANALYTICS=true
CACHE_TTL_SECONDS=300
```

## Features

### ✅ Current Features

- 📊 **Real-time Analytics** - View booking statistics and revenue
- 🔔 **Notification Queue** - Extensible notification system
- 🏷️ **Status Management** - Update booking statuses
- ⚡ **REST API** - All functionality exposed as JSON APIs
- 💾 **Shared Database** - Both services use the same SQLite database
- 🏥 **Health Checks** - Monitor service health

### 🚀 Future Features (Extensible)

- 📧 Email notifications (Gmail, SendGrid)
- 📱 SMS notifications (Twilio)
- 💬 WhatsApp notifications
- 📈 Advanced analytics and dashboards
- 🔔 Push notifications
- 📅 Appointment scheduling
- 🤖 AI-powered booking recommendations

## Troubleshooting

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find and kill process on port 3000
lsof -ti:3000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :3000   # Windows

# Change WORKER_PORT in worker/.env to a different port
```

### Database Locked

**Error:** `SQLITE_ERROR: database is locked`

**Solution:**
- Ensure only one Flask instance is running
- Close any other SQLite connections
- Restart both services

### Connection Refused

**Error:** `Error: connect ECONNREFUSED 127.0.0.1:3000`

**Solution:**
- Check if Worker is running: `curl http://localhost:3000/api/worker/health`
- Check worker logs: `cat worker/worker.out.log`
- Restart the Worker service

### Module Not Found

**Error:** `Cannot find module 'express'`

**Solution:**
```bash
cd worker
npm install
npm start
```

## Deployment

### Vercel Deployment

1. **Build Configuration**
   ```json
   {
     "buildCommand": "cd worker && npm install",
     "outputDirectory": "worker"
   }
   ```

2. **Environment Variables**
   - Set `WORKER_PORT` to a dynamic port provided by Vercel
   - Set `DATABASE_PATH` to an absolute path or use Vercel Blob

3. **Multiple Services**
   - Use Vercel Functions for the Worker API
   - Keep Flask as a separate deployment

### Docker Deployment

```dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy both Flask and Node.js app
COPY . .
WORKDIR /app/worker

RUN npm install

EXPOSE 3000

CMD ["npm", "start"]
```

### Production Checklist

- ✅ Set up database backups
- ✅ Enable error logging and monitoring
- ✅ Configure email/SMS providers for notifications
- ✅ Set up SSL/TLS for HTTPS
- ✅ Implement rate limiting on APIs
- ✅ Add authentication to admin endpoints
- ✅ Set up health checks and monitoring

## Development

### Adding New Endpoints

Edit `worker/src/index.js`:

```javascript
/**
 * New custom endpoint
 */
app.get('/api/worker/custom', async (req, res) => {
  try {
    const result = await db.all('SELECT * FROM bookings');
    res.json({ success: true, data: result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});
```

### Adding Notifications

Extend the notification endpoint in `worker/src/index.js`:

```javascript
async function sendEmailNotification(booking) {
  // Integrate with nodemailer or SendGrid
}

async function sendSmsNotification(booking) {
  // Integrate with Twilio or AWS SNS
}

app.post('/api/worker/bookings/:id/notify', async (req, res) => {
  const { method } = req.body;
  const booking = await db.get('SELECT * FROM bookings WHERE id = ?', id);
  
  if (method === 'email' || !method) {
    await sendEmailNotification(booking);
  }
  if (method === 'sms' || !method) {
    await sendSmsNotification(booking);
  }
  
  res.json({ success: true });
});
```

## Support & Documentation

- **Flask App**: See main `README.md`
- **Worker Service**: See `worker/README.md`
- **Issues**: Check logs in `server.err.log` and `worker/worker.err.log`

## License

MIT

---

**Last Updated:** June 24, 2024
