# RapidRepair.in

Flask and SQLite web app for AC service, appliance repair, and home-care bookings, with Node.js background worker for analytics and notifications.

## Quick Start

### Flask App Only (Python)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000`.

### Flask + Node.js Worker (Recommended) ✨

**Linux/macOS:**
```bash
chmod +x run-services.sh
./run-services.sh
```

**Windows PowerShell:**
```powershell
.\run-services.ps1
```

This starts both services:
- 📊 Flask app: `http://127.0.0.1:5000`
- ⚙️ Worker API: `http://127.0.0.1:3000`

## Features

### Flask Backend
- AC service-first homepage for `rapidrepair.in`
- SQLite service catalog and booking table
- ML-style quote estimator in `ml_estimator.py`
- Booking confirmation page
- Admin booking list at `/admin/bookings`
- JSON APIs at `/api/services` and `/api/estimate`

### Node.js Worker Service ✨ NEW
- 📊 Real-time booking analytics and statistics
- 🔔 Booking notifications management (extensible)
- 🏷️ Booking status updates
- ⚡ REST API for all operations
- 💾 Shared SQLite database
- 🏥 Health check endpoints

## Documentation

- **[Node.js Integration Guide](./NODEJS_INTEGRATION.md)** - Complete setup and usage guide
- **[Worker API Reference](./worker/README.md)** - Detailed endpoint documentation

## Quick API Examples

### Get Booking Analytics
```bash
curl http://localhost:3000/api/worker/analytics
```

### Update Booking Status
```bash
curl -X POST http://localhost:3000/api/worker/bookings/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "Confirmed"}'
```

### Send Notification
```bash
curl -X POST http://localhost:3000/api/worker/bookings/1/notify \
  -H "Content-Type: application/json" \
  -d '{"method": "sms"}'
```

See **[NODEJS_INTEGRATION.md](./NODEJS_INTEGRATION.md)** for complete examples.
