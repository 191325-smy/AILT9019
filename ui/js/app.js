// AILT9019 Teammate Matcher - UI JavaScript
// Connects to FastAPI backend at http://localhost:8000

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// State
let currentUser = null;
let authToken = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupEventListeners();
    if (window.location.pathname.endsWith('dashboard.html')) loadDashboard();
});

// Check authentication status from localStorage
function checkAuth() {
    const storedToken = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('currentUser');

    if (storedToken && storedUser) {
        authToken = storedToken;
        currentUser = JSON.parse(storedUser);
        updateNavbar();
    }

    // Redirect if needed
    const currentPage = window.location.pathname.split('/').pop();
    if (['dashboard.html', 'edit-profile.html', 'results.html'].includes(currentPage) && !currentUser) {
        window.location.href = 'index.html';
    }
}

// Update navbar based on auth status
function updateNavbar() {
    const navLinks = document.getElementById('nav-links');
    if (navLinks && currentUser) {
        navLinks.innerHTML = `
            <a href="dashboard.html">Dashboard</a>
            <a href="edit-profile.html">Edit Profile</a>
            <a href="#" onclick="logout(); return false;">Logout (${escapeHtml(currentUser.username)})</a>
        `;
    }
}

// Setup event listeners
function setupEventListeners() {
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Register form
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    // Edit profile form
    const editProfileForm = document.getElementById('edit-profile-form');
    if (editProfileForm) {
        editProfileForm.addEventListener('submit', handleEditProfile);
        populateEditForm();
    }

    // Match button
    const matchBtn = document.getElementById('match-btn');
    if (matchBtn) {
        matchBtn.addEventListener('click', runMatching);
    }
}

// API call helper
async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    };

    if (authToken) {
        config.headers['Authorization'] = `Bearer ${authToken}`;
    }

    const response = await fetch(url, config);

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        const detail = Array.isArray(error.detail)
            ? error.detail.map(item => `${item.loc.slice(1).join('.')}: ${item.msg}`).join('; ')
            : error.detail;
        const failure = new Error(detail || `HTTP ${response.status}`);
        failure.status = response.status;
        throw failure;
    }

    return response;
}

// Handle login
async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('authToken', authToken);

        // Get user info
        const meResponse = await apiCall('/auth/me');
        const user = await meResponse.json();

        currentUser = user;
        localStorage.setItem('currentUser', JSON.stringify(user));

        showAlert('success', `Welcome back, ${user.username}!`);
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 500);
    } catch (error) {
        showAlert('error', error.message || 'Login failed. Please check your credentials.');
    }
}

// Handle register
async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        await apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        // The account and profile are separate API resources.
        const loginResponse = await apiCall('/auth/login', {
            method: 'POST', body: JSON.stringify({ username, password })
        });
        authToken = (await loginResponse.json()).access_token;
        localStorage.setItem('authToken', authToken);
        const meResponse = await apiCall('/auth/me');
        currentUser = await meResponse.json();
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        await apiCall('/profiles/me', {
            method: 'PUT', body: JSON.stringify(profileFromForm())
        });
        showAlert('success', 'Account and profile saved successfully!');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 500);
    } catch (error) {
        if (currentUser && authToken) {
            showAlert('error', `Account created, but profile was not saved: ${error.message}. Open Edit Profile to complete it.`);
            updateNavbar();
        } else {
            showAlert('error', error.message || 'Registration failed.');
        }
    }
}

function profileFromForm() {
    return {
        display_name: document.getElementById('display_name').value,
        contact_info: document.getElementById('contact_info').value || null,
        city: document.getElementById('city').value,
        preferred_role: document.getElementById('preferred_role').value,
        languages: document.getElementById('languages').value.split(',').map(l => l.trim()).filter(Boolean)
    };
}

async function loadDashboard() {
    if (!currentUser || !authToken) return;
    document.getElementById('profile-username').textContent = currentUser.username;
    document.getElementById('user-display-name').textContent = currentUser.username;
    try {
        const response = await apiCall('/profiles/me');
        const profile = await response.json();
        document.getElementById('user-display-name').textContent = profile.display_name;
        document.getElementById('profile-city').textContent = profile.city;
        document.getElementById('profile-role').textContent = profile.preferred_role;
        document.getElementById('profile-languages').textContent = profile.languages.join(', ') || 'Not specified';
        document.getElementById('profile-contact').textContent = profile.contact_info || 'Not provided';
        const badge = document.getElementById('profile-status');
        badge.textContent = profile.in_team ? 'Already in a team' : 'Looking for teammates';
        badge.className = profile.in_team ? 'badge badge-success' : 'badge badge-warning';
    } catch (error) {
        showAlert('error', error.status === 404 ? 'Please open Edit Profile and save your information before matching.' : error.message);
    }
}

function escapeHtml(value) {
    const span = document.createElement('span');
    span.textContent = String(value ?? '');
    return span.innerHTML.replaceAll('"', '&quot;').replaceAll("'", '&#39;');
}

// Handle edit profile
async function handleEditProfile(e) {
    e.preventDefault();

    const display_name = document.getElementById('display_name').value;
    const contact_info = document.getElementById('contact_info').value;
    const city = document.getElementById('city').value;
    const preferred_role = document.getElementById('preferred_role').value;
    const languages = document.getElementById('languages').value
        .split(',')
        .map(l => l.trim())
        .filter(l => l);

    try {
        await apiCall('/profiles/me', {
            method: 'PUT',
            body: JSON.stringify({
                display_name,
                contact_info: contact_info || null,
                city,
                preferred_role,
                languages
            })
        });

        showAlert('success', 'Profile updated successfully!');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);
    } catch (error) {
        showAlert('error', error.message || 'Failed to update profile.');
    }
}

// Populate edit form with current user data
async function populateEditForm() {
    if (!currentUser || !authToken) return;

    try {
        const response = await apiCall('/profiles/me');
        const profile = await response.json();

        document.getElementById('display_name').value = profile.display_name || '';
        document.getElementById('contact_info').value = profile.contact_info || '';
        document.getElementById('city').value = profile.city || 'HK';
        document.getElementById('preferred_role').value = profile.preferred_role || 'Other';
        document.getElementById('languages').value = (profile.languages || []).join(', ');
        document.getElementById('in_team').checked = profile.in_team === 1;
    } catch (error) {
        console.error('Failed to load profile:', error);
    }
}

// Run matching algorithm
async function runMatching() {
    if (!currentUser || !authToken) {
        showAlert('error', 'Please log in first.');
        return;
    }

    try {
        const response = await apiCall('/matches', {
            method: 'POST'
        });

        const data = await response.json();

        // Store results for results page
        localStorage.setItem('currentMatches', JSON.stringify(data.picks));
        localStorage.setItem('matchStats', JSON.stringify(data.stats));
        localStorage.setItem('filterSummary', JSON.stringify(data.filter_summary));
        localStorage.setItem('matchSource', data.source);

        window.location.href = 'results.html';
    } catch (error) {
        showAlert('error', error.message || 'Failed to run matching.');
    }
}

// Logout
async function logout() {
    if (authToken) {
        try {
            await apiCall('/auth/logout', {
                method: 'POST'
            });
        } catch (error) {
            console.error('Logout API call failed:', error);
        }
    }

    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('currentMatches');
    localStorage.removeItem('matchStats');
    localStorage.removeItem('filterSummary');
    localStorage.removeItem('matchSource');

    authToken = null;
    currentUser = null;

    showAlert('info', 'You have been logged out.');
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 500);
}

// Show alert message
function showAlert(type, message) {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;

    alertContainer.appendChild(alert);

    // Auto remove after 3 seconds
    setTimeout(() => {
        alert.remove();
    }, 3000);
}

// Load results page data
function loadResults() {
    const matches = JSON.parse(localStorage.getItem('currentMatches') || '[]');
    const stats = JSON.parse(localStorage.getItem('matchStats') || '{}');
    const filterSummary = JSON.parse(localStorage.getItem('filterSummary') || '{}');
    const source = localStorage.getItem('matchSource') || 'unknown';

    if (!currentUser) {
        window.location.href = 'index.html';
        return;
    }

    // Update user info
    document.getElementById('user-name').textContent = currentUser.username;

    // Load profile for display
    apiCall('/profiles/me')
        .then(response => response.json())
        .then(profile => {
            document.getElementById('user-city').textContent = profile.city;
            document.getElementById('user-role').textContent = profile.preferred_role;
        })
        .catch(error => {
            console.error('Failed to load profile:', error);
        });

    // Update stats
    document.getElementById('stat-total').textContent = stats.total_pool || 0;
    document.getElementById('stat-eligible').textContent = stats.eligible || 0;
    document.getElementById('stat-filtered').textContent = stats.filtered_out || 0;
    document.getElementById('stat-recommended').textContent = matches.length;

    // Update source badge
    const sourceBadge = document.querySelector('.source-badge');
    if (sourceBadge) {
        if (source.startsWith('fallback')) {
            sourceBadge.textContent = '⚙️ Deterministic Fallback';
        } else if (source === 'empty') {
            sourceBadge.textContent = 'No eligible candidates';
        } else {
            sourceBadge.textContent = '🤖 AI Model';
        }
    }

    // Update filter summary
    const filterTags = document.getElementById('filter-tags');
    if (filterTags && Object.keys(filterSummary).length > 0) {
        filterTags.innerHTML = Object.entries(filterSummary)
            .map(([reason, count]) => `<span class="filter-tag">${escapeHtml(count)} ${escapeHtml(reason)}</span>`)
            .join('');
    }

    // Update picks
    const picksGrid = document.getElementById('picks-grid');
    if (picksGrid) {
        if (matches.length === 0) {
            picksGrid.innerHTML = '<div class="no-results"><h3>No matches found</h3></div>';
        } else {
            picksGrid.innerHTML = matches.map(match => `
                <div class="pick-card">
                    <div class="pick-rank">#${match.rank}</div>
                    <div class="pick-content">
                        <div class="pick-header">
                            <h3>${escapeHtml(match.display_name)}</h3>
                            <span class="badge badge-role">${escapeHtml(match.preferred_role)}</span>
                        </div>
                        <div class="pick-details">
                            <div class="detail-item">
                                <span class="detail-icon">📍</span>
                                <span>${escapeHtml(match.city)}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-icon"></span>
                                <span>${escapeHtml(match.contact_info || 'Not provided')}</span>
                            </div>
                            ${match.shared_languages && match.shared_languages.length > 0 ? `
                                <div class="detail-item">
                                    <span class="detail-icon">🗣️</span>
                                    <span>${escapeHtml(match.shared_languages.join(', '))}</span>
                                </div>
                            ` : ''}
                            ${match.role_fit === 'complement' ? `
                                <div class="detail-item">
                                    <span class="detail-icon">✨</span>
                                    <span class="complement-badge">Complementary Role</span>
                                </div>
                            ` : ''}
                        </div>
                        <div class="pick-reason">
                            <strong>Why:</strong> ${escapeHtml(match.reason)}
                        </div>
                        <div class="pick-actions">
                            <a href="mailto:${escapeHtml(match.contact_info || '')}" class="btn btn-sm btn-secondary">
                                📧 Contact
                            </a>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    }
}

// Initialize results page
if (window.location.pathname.includes('results.html')) {
    document.addEventListener('DOMContentLoaded', loadResults);
}
