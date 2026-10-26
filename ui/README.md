# AILT9019 Teammate Matcher - UI

Pure frontend UI interface for the Teammate Matcher project.

## File Structure

```
ui/
├── index.html          # Login page
├── register.html       # Registration page
├── dashboard.html      # Main dashboard
├── results.html        # Match results display
├── edit-profile.html   # Profile editor
├── css/
│   └── style.css       # Styling
├── js/
│   └── app.js          # JavaScript logic
└── data/
    └── mock-data.json  # Mock data for demo
```

## Usage

Start the backend from the repository root using `start-backend.bat` on
Windows or `sh start-backend.sh` on macOS/Linux. In a second terminal, run
`start-frontend.bat` or `sh start-frontend.sh`, respectively.

Or start the frontend manually while the backend is running:

```bash
# Python 3
cd ui
python -m http.server 8001

# Then visit http://localhost:8001
```

Register a new username with a password of at least 8 characters and synthetic
profile details. The UI registers, logs in and saves the profile through the
real API. Seeded accounts such as `alice_chen` have placeholder password hashes;
`alice_chen / demo` is not a usable login. Use the local HTTP server instead of
opening the HTML file directly.

## Pages

### 1. Login Page (index.html)
- User login form
- Registration and synthetic-data guidance
- Registration link

### 2. Register Page (register.html)
- New user registration form
- Fields: username, password, display name, email, city, role, languages

### 3. Dashboard (dashboard.html)
- Display current user profile
- Run matching algorithm button
- Matching workflow explanation

### 4. Match Results (results.html)
- Statistics (total pool, eligible, filtered, recommended)
- Filter reason summary
- Recommended teammates list (rank, role, shared languages, match reason)
- Contact button

### 5. Edit Profile (edit-profile.html)
- Modify personal profile
- Update city, role, languages, etc.

## Design Features

- **Responsive Design**: Adapts to desktop and mobile devices
- **Modern UI**: Card layout, gradient colors, shadow effects
- **Interactive Feedback**: Form validation, success/error alerts
- **API Integration**: Authentication, saved profiles and matching use FastAPI;
  `data/mock-data.json` is a legacy fixture, not the active data source.

## Tech Stack

- HTML5
- CSS3 (custom styles, no framework)
- Vanilla JavaScript (no framework)
- LocalStorage (the API-issued login token and latest results)

## Notes

The frontend calls the backend at `http://localhost:8000`. The default backend
CORS configuration allows `http://localhost:8001` and `http://127.0.0.1:8001`.
Profile changes persist in SQLite; matching results depend on the saved profile.
Team status is managed by fixture data. Time-overlap preferences and mutual
contact consent remain future work. Use synthetic contacts only in the demo.

## Screenshots

(Open the local website to view the interface.)

---

AILT9019 - AI Literacy for Computing and Data Science | HKU 2026-27
