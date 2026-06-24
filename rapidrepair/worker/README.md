# RapidRepair Node.js Worker Service

Background worker service for RapidRepair bookings, handling notifications, analytics, and booking management.

## Features

- 📊 Real-time booking analytics and statistics
- 🔔 Booking notifications management (extensible for email/SMS)
- 🏷️ Booking status updates
- ⚡ Express REST API for worker operations
- 💾 SQLite database integration with `better-sqlite3`
- 🏥 Health check endpoints

## Setup

### Installation

```bash
npm install
```

### Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Key variables:**
- `WORKER_PORT=3000` - Port for worker API
- `FLASK_API_URL=http://127.0.0.1:5000` - Flask backend URL
- `DATABASE_PATH=../rapidrepair.db` - Path to SQLite database
- `CACHE_TTL_SECONDS=300` - Cache time-to-live

## Running

### Development Mode

```bash
npm run dev
```

Watches for file changes and restarts automatically.

### Production Mode

```bash
npm start
```

## API Endpoints

### Health Check
```http
GET /api/worker/health
```

Returns worker health status and uptime.

**Response:**
```json
{
  "status": "healthy",
  "service": "RapidRepair Worker",
  "uptime": 123.45,
  "timestamp": "2024-06-24T10:30:00.000Z"
}
```

---

### Get Bookings
```http
GET /api/worker/bookings?status=New
```

Fetch bookings with optional status filtering.

**Query Parameters:**
- `status` (optional) - Filter by status (New, Confirmed, In Progress, Completed, Cancelled)

**Response:**
```json
{
  "success": true,
  "count": 5,
  "bookings": [
    {
      "id": 1,
      "customer_name": "John Doe",
      "phone": "9876543210",
      "service_name": "AC General Service",
      "category": "AC Service",
      "estimate_price": 499,
      "estimate_minutes": 45,
      "status": "New",
      "created_at": "2024-06-24T10:00:00"
    }
  ],
  "timestamp": "2024-06-24T10:30:00.000Z"
}
```

---

### Get Analytics
```http
GET /api/worker/analytics
```

Fetch comprehensive booking analytics and statistics.

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
      { "status": "Completed", "count": 15 }
    ],
    "bookingsByService": [
      { "name": "AC General Service", "count": 12 },
      { "name": "AC Repair Visit", "count": 6 }
    ]
  },
  "timestamp": "2024-06-24T10:30:00.000Z"
}
```

---

### Update Booking Status
```http
POST /api/worker/bookings/:id/status
```

Update the status of a booking.

**Request Body:**
```json
{
  "status": "Confirmed"
}
```

**Valid statuses:**
- `New` - Initial status
- `Confirmed` - Confirmed by admin
- `In Progress` - Technician is on the way
- `Completed` - Service completed
- `Cancelled` - Booking cancelled

**Response:**
```json
{
  "success": true,
  "message": "Booking status updated to Confirmed",
  "booking": { ... }
}
```

---

### Queue Booking Notification
```http
POST /api/worker/bookings/:id/notify
```

Queue a notification for a booking (extensible for email/SMS).

**Request Body:**
```json
{
  "method": "sms"
}
```

**Supported methods:**
- `email` - Email notification
- `sms` - SMS notification
- `whatsapp` - WhatsApp notification
- Omit for all available channels

**Response:**
```json
{
  "success": true,
  "message": "Notification queued successfully",
  "notification": {
    "booking_id": 1,
    "customer_name": "John Doe",
    "service_name": "AC General Service",
    "phone": "9876543210",
    "message": "Your booking for AC General Service is confirmed. Total: ₹499",
    "timestamp": "2024-06-24T10:30:00.000Z"
  }
}
```

---

## Running Multiple Services

### Linux/macOS

Run the multi-service launcher script:

```bash
chmod +x run-services.sh
./run-services.sh
```

### Windows PowerShell

```powershell
.\run-services.ps1
```

This will start both Flask (port 5000) and Worker (port 3000) services.

## Integration with Flask App

The worker service accesses the same SQLite database (`rapidrepair.db`) as the Flask app. Both services:

1. **Read** from the shared database
2. **Update** booking statuses and metadata
3. **Query** for analytics and reporting

No additional configuration is needed—the worker simply shares the database file path.

## Extensibility

The worker is designed to be extended:

### Adding Email Notifications

Modify `src/index.js` in the `/api/worker/bookings/:id/notify` endpoint:

```javascript
if (method === 'email' || !method) {
  sendEmail(booking.customer_name, booking.phone, notification);
}
```

### Adding Cron Jobs

Use a package like `node-cron` to schedule periodic tasks:

```javascript
import cron from 'node-cron';

cron.schedule('0 9 * * *', () => {
  // Send daily booking summary
});
```

### Adding Message Queue

Integrate with Redis/RabbitMQ for job queuing:

```javascript
import Bull from 'bull';

const notificationQueue = new Bull('notifications');
notificationQueue.process(async (job) => {
  // Process notification
});
```

## Troubleshooting

### Database is locked
- Ensure only one Flask instance is running
- Check that previous node processes are terminated

### Port already in use
- Change `WORKER_PORT` in `.env`
- Or kill the process: `lsof -ti:3000 | xargs kill -9` (macOS/Linux)

### Cannot find module
- Reinstall dependencies: `npm install`
- Delete `node_modules` and `package-lock.json`, then reinstall

## License

MIT
