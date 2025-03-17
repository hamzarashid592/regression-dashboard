# 🐛 Mantis Ticket Sync Automation

A Python Flask-based automation system that syncs Mantis tickets to a Google Sheet.\
Includes a minimalist web interface for:

- Manual job triggering
- Live job progress/status display
- Configuration management (update Sheet Key, Filter ID, etc.)
- Downloadable logs
- Job scheduling with dynamic interval control

---

## 📂 Project Structure

```
mantis_ticket_sync/
├── app.py                      # Flask server & routing
├── scheduler.py                # APScheduler job handler
├── /clients/                   # Mantis & Google Sheets API interaction
│   ├── mantis_operations.py
│   └── google_sheets_operations.py
├── /processors/                # Ticket processing logic
│   └── regression_progress_updater.py
├── /templates/                 # Flask HTML templates
│   ├── index.html              # Main dashboard
│   └── config.html             # Config management UI
├── /static/                    # JS and CSS files
│   ├── main.js                 # JS for triggering jobs & updating status
│   ├── config.js               # JS for config page management
│   └── style.css               # Styling for UI
├── /logs/                      # Logs directory (auto-generated)
│   └── regression_progress_YYYY-MM-DD.log
├── /logging/                   # Logger setup
│   └── logging_config.py
├── /utils/                     # Helper functions
│   └── utils.py
├── config.json                 # Editable config file (Sheet Keys, Filter IDs, etc.)
├── credentials.json            # Google Sheets service account credentials
├── README.md                   # Project documentation
└── requirements.txt            # Python dependencies
```

---

## 🚀 Features

- 📉 Mantis Tickets to Google Sheets Sync
- ✅ Manual & Scheduled Sync Jobs
- 🔹 Live Progress Bar & Status
- ⚙️ Configurable Google Sheet, Mantis Filter, and Interval
- 📄 Downloadable Daily Logs
- 🔄 Simple, Clean UI

---

## ⚙️ Installation & Setup

### 1. Clone the Repo

```bash
git clone https://github.com/your-repo/mantis-ticket-sync.git
cd mantis-ticket-sync
```

### 2. Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare Configurations

#### Google Service Account

- Place your `credentials.json` file in the project root.

#### config.json

```json
{
    "REGRESSION_SHEET_KEY": "your-google-sheet-key",
    "MANTIS_TICKETS_NEXUS_E6": "Sheet Name",
    "REGRESSION_FILTER_ID": "123456",
    "MANTIS_BASE_URL": "https://mantis.yourdomain.com",
    "MANTIS_AUTH_TOKEN": "your-mantis-token",
    "JOB_INTERVAL_MINUTES": 60,
    "GS_CREDENTIAL_FILE": "credentials.json"
}
```

---

## ▶️ Running the App

```bash
python app.py
```

The app runs on:

```
http://localhost:5001
```

#### Flask Ports

- Merge Automation: `5000`
- Mantis Sync Automation: `5001`

Adjust `app.py` port if necessary:

```python
app.run(host='0.0.0.0', port=5001)
```

---

## 🔢 Web UI Overview

### Main Dashboard `/`

- **Run Sync Now**: Trigger Mantis ➔ Google Sheets sync manually.
- **Progress Bar**: Displays job execution progress.
- **Next Scheduled Run**: Shows the next job run time.
- **Time Left**: Live countdown timer to the next job run.
- **Download Logs**: Get daily logs (date-based).

### Configurations Page `/config`

- Edit **Sheet Key**, **Sheet Name**, **Mantis Filter ID**, and **Job Interval**.
- Updates take effect immediately.
- Dynamically reschedules jobs if interval is changed.

---

## 🔄 Scheduling Jobs

- APScheduler handles automatic job execution.
- Modify default interval in `config.json` (`JOB_INTERVAL_MINUTES`).
- Or update dynamically via the **config page** UI.

---

## 📃 Logs

- Logs are generated daily in `/logs/`

```
/logs/regression_progress_YYYY-MM-DD.log
```

- Download logs via the UI or directly from the logs folder.

---

## ✅ Requirements

- Python 3.8+
- Flask
- APScheduler
- gspread
- oauth2client
- requests
- dateutil

Install via:

```bash
pip install -r requirements.txt
```

---

## 🔐 Security Suggestions (Optional)

- Add **Authentication** to protect the UI and config pages.
- Dockerize for **containerized deployment**.
- Use **HTTPS** for secure communication.

---

## 🔧 Future Improvements

- Job history dashboard (success/failure tracking)
- Email/Slack notifications on job status
- Pause/Resume job scheduler via UI
- User access control (admin/non-admin features)

---

## 👨‍💻 Authors

- Hamza Rashid
- Regression - Northstar Technologies

---

## 📄 License

N/A

---

🔹 *Made with ❤️ for Mantis Sync!*
