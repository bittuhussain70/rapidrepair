# RapidRepair Node.js Integration - Setup Summary

## ✅ What Was Added

Your RapidRepair project now includes a **Node.js Worker Service** running alongside the Flask backend. This adds powerful analytics, status management, and notification capabilities.

### New Files Created

```
rapidrepair/
├── worker/                          # Node.js Worker Service
│   ├── src/
│   │   └── index.js                # Main worker application
│   ├── package.json                # Node.js dependencies
│   ├── .env.example                # Environment configuration template
│   └── README.md                   # Worker API documentation
├── run-services.sh                 # Linux/macOS multi-service launcher
├── run-services.ps1                # Windows PowerShell launcher
├── NODEJS_INTEGRATION.md           # Complete integration guide
└── SETUP_SUMMARY.md               # This file
```

## 🚀 Running the Services

### All-in-One Command (Recommended)

**Linux/macOS:**
```bash
chmod +x run-services.sh
./run-services.sh
```

**Windows PowerShell:**
```powershell
.\run-services.ps1
```

### Manual Mode

**Terminal 1 - Flask App:**
```bash
python app.py
```

**Terminal 2 - Node.js Worker:**
```bash
cd worker
npm install
npm start
```

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Flask App** | `http://127.0.0.1:5000` | Web UI, bookings, admin panel |
| **Worker API** | `http://127.0.0.1:3000` | Analytics, notifications, status updates |
| **Health Check** | `http://127.0.0.1:3000/api/worker/health` | Verify worker is running |

## 📊 Key Features Added

### 1. **Real-Time Analytics**
Get comprehensive booking statistics:
```bash
curl http://localhost:3000/api/worker/analytics
```

Returns:
- Total bookings and revenue
- Bookings by status
- Bookings by service
- Average quote price
- Average service time

### 2. **Booking Status Management**
Update booking status from any client:
```bash
curl -X POST http://localhost:3000/api/worker/bookings/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "Confirmed"}'
```

Valid statuses: `New`, `Confirmed`, `In Progress`, `Completed`, `Cancelled`

### 3. **Notification Queue**
Queue notifications for bookings (extensible):
```bash
curl -X POST http://localhost:3000/api/worker/bookings/1/notify \
  -H "Content-Type: application/json" \
  -d '{"method": "sms"}'
```

Supported methods: `email`, `sms`, `whatsapp`

### 4. **Booking Filtering**
Get bookings by status:
```bash
curl "http://localhost:3000/api/worker/bookings?status=New"
```

## 📦 Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Flask Templates (HTML/CSS/JS) |
| **Backend - Web** | Flask 3.0+ |
| **Backend - Worker** | Node.js 20+ with Express |
| **Database** | SQLite 3 |
| **Estimate Engine** | Python ML module |

## 🔧 Configuration

### Worker Environment (worker/.env)

```env
WORKER_PORT=3000                    # Worker API port
FLASK_API_URL=http://127.0.0.1:5000 # Flask backend URL
DATABASE_PATH=../rapidrepair.db     # Shared database path
CACHE_TTL_SECONDS=300               # Cache duration
ENABLE_EMAIL_NOTIFICATIONS=false    # Feature flag
ENABLE_ANALYTICS=true               # Feature flag
```

Copy from `.env.example`:
```bash
cp worker/.env.example worker/.env
```

## 📈 Database

Both services share the same SQLite database (`rapidrepair.db`):

```
┌─ Tables ──────────────────┐
│ services                  │
│  - id                     │
│  - slug, name, price      │
│  - category, badge        │
│  - description, duration  │
│                           │
│ bookings                  │
│  - id                     │
│  - customer_name, phone   │
│  - service_slug, status   │
│  - estimate_price/minutes │
│  - created_at, ac_type    │
│  - tonnage, unit_age      │
│  - urgency, preferred_slot│
└───────────────────────────┘
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# macOS/Linux: Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Windows: Find and kill process on port 3000
netstat -ano | findstr :3000
```

### "Cannot find module" Error
```bash
cd worker
npm install
npm start
```

### Worker Not Connecting to Database
Ensure both services see the same database:
```bash
ls -l rapidrepair.db
ls -l worker/rapidrepair.db
```

## 📚 Documentation

- **[NODEJS_INTEGRATION.md](./NODEJS_INTEGRATION.md)** - Complete guide with examples
- **[worker/README.md](./worker/README.md)** - Detailed API reference
- **[app.py](./app.py)** - Flask application
- **[ml_estimator.py](./ml_estimator.py)** - Quote estimation logic

## 🚢 Deployment

### Vercel

The Worker service can be deployed as a Vercel Function:

```javascript
// api/worker.js
export default async function handler(req, res) {
  // Route to worker endpoints
}
```

### Docker

```dockerfile
FROM node:20-alpine
WORKDIR /app/worker
COPY package*.json ./
RUN npm install
COPY src ./src
EXPOSE 3000
CMD ["npm", "start"]
```

## 🔮 Future Extensions

The worker service is designed to be extended with:

- **Email Notifications** - Integrate Nodemailer or SendGrid
- **SMS Notifications** - Integrate Twilio or AWS SNS
- **Cron Jobs** - Schedule periodic tasks (daily summaries)
- **Message Queue** - Redis/RabbitMQ for reliable job processing
- **Advanced Analytics** - Charts, trends, forecasting
- **Real-time Updates** - WebSocket support for live dashboards
- **Machine Learning** - Predictive analytics and recommendations

## 📞 Support

### Check Service Status
```bash
curl http://localhost:3000/api/worker/health
```

### View Logs
```bash
# Flask logs
cat server.out.log
cat server.err.log

# Worker logs
cat worker/worker.out.log
cat worker/worker.err.log
```

### Test Connectivity
```bash
# Test Flask
curl http://127.0.0.1:5000/api/services

# Test Worker
curl http://127.0.0.1:3000/api/worker/bookings
```

## ✨ What's Next?

1. **Integrate with Admin Dashboard** - Show analytics in Flask admin panel
2. **Add Email Notifications** - Send booking confirmations via email
3. **Implement Real-time Updates** - WebSocket for live booking updates
4. **Deploy to Production** - Use Vercel or your preferred platform
5. **Monitor Performance** - Add metrics and health dashboards

---

**Created:** June 24, 2024  
**Status:** ✅ Running and Ready to Use  
**Services:** Flask (5000) + Worker (3000)
