# RapidRepair.in

Flask and SQLite web app for AC service, appliance repair, and home-care bookings.

## Run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Features

- AC service-first homepage for `rapidrepair.in`
- SQLite service catalog and booking table
- ML-style quote estimator in `ml_estimator.py`
- Booking confirmation page
- Admin booking list at `/admin/bookings`
- JSON APIs at `/api/services` and `/api/estimate`
