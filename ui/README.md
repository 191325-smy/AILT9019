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

### Direct Browser Open

1. Open `index.html` file in browser
2. Use demo account to login:
   - Username: `alice_chen`
   - Password: `demo`

### Or Use Local Server

```bash
# Python 3
cd ui
python -m http.server 8000

# Then visit http://localhost:8000
```

## Pages

### 1. Login Page (index.html)
- User login form
- Demo account hints
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
- **Mock Data**: Uses JSON file to simulate backend data

## Tech Stack

- HTML5
- CSS3 (custom styles, no framework)
- Vanilla JavaScript (no framework)
- LocalStorage (simulated user sessions)

## Notes

This is a pure frontend demo UI with all mock data. For production use:
- Connect to backend API
- Real user authentication system
- Actual matching algorithm calls

## Screenshots

(Open in browser to view actual效果)

---

AILT9019 - AI Literacy for Computing and Data Science | HKU 2026-27
