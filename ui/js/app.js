// AILT9019 Teammate Matcher - UI JavaScript

// Mock data storage
let currentUser = null;
let mockData = null;

// Load mock data
async function loadMockData() {
    try {
        const response = await fetch('data/mock-data.json');
        mockData = await response.json();
        console.log('Mock data loaded:', mockData);
    } catch (error) {
        console.error('Failed to load mock data:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadMockData();
    checkAuth();
    setupEventListeners();
});

// Check authentication status
function checkAuth() {
    const storedUser = localStorage.getItem('currentUser');
    if (storedUser) {
        currentUser = JSON.parse(storedUser);
        updateNavbar();
    }

    // Redirect if needed
    const currentPage = window.location.pathname.split('/').pop();
    if (currentPage === 'dashboard.html' && !currentUser) {
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
            <a href="#" onclick="logout()">Logout (${currentUser.username})</a>
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

// Handle login
function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Mock authentication
    const user = mockData.users.find(u => u.username === username && u.password === password);

    if (user) {
        currentUser = user;
        localStorage.setItem('currentUser', JSON.stringify(user));
        showAlert('success', `Welcome back, ${user.display_name}!`);
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 500);
    } else {
        showAlert('error', 'Invalid username or password. Try: alice_chen / demo');
    }
}

// Handle register
function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const display_name = document.getElementById('display_name').value;

    // Mock registration
    showAlert('success', 'Registration successful! Please log in.');
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 1000);
}

// Handle edit profile
function handleEditProfile(e) {
    e.preventDefault();
    showAlert('success', 'Profile updated successfully!');
    setTimeout(() => {
        window.location.href = 'dashboard.html';
    }, 1000);
}

// Populate edit form with current user data
function populateEditForm() {
    if (!currentUser) return;

    document.getElementById('display_name').value = currentUser.display_name || '';
    document.getElementById('contact_info').value = currentUser.contact_info || '';
    document.getElementById('city').value = currentUser.city || 'HK';
    document.getElementById('preferred_role').value = currentUser.preferred_role || 'Other';
    document.getElementById('languages').value = (currentUser.languages || []).join(', ');
    document.getElementById('in_team').checked = currentUser.in_team || false;
}

// Run matching algorithm
function runMatching() {
    if (!currentUser) {
        showAlert('error', 'Please log in first.');
        return;
    }

    // Mock matching - redirect to results page with user data
    const matches = mockData.sample_matches[currentUser.username] || [];
    localStorage.setItem('currentMatches', JSON.stringify(matches));
    localStorage.setItem('matchStats', JSON.stringify(mockData.stats));
    localStorage.setItem('filterSummary', JSON.stringify(mockData.filter_summary));

    window.location.href = 'results.html';
}

// Logout
function logout() {
    localStorage.removeItem('currentUser');
    localStorage.removeItem('currentMatches');
    localStorage.removeItem('matchStats');
    localStorage.removeItem('filterSummary');
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

    if (!currentUser) {
        window.location.href = 'index.html';
        return;
    }

    // Update user info
    document.getElementById('user-name').textContent = currentUser.display_name;
    document.getElementById('user-city').textContent = currentUser.city;
    document.getElementById('user-role').textContent = currentUser.preferred_role;

    // Update stats
    document.getElementById('stat-total').textContent = stats.total_pool || 0;
    document.getElementById('stat-eligible').textContent = stats.eligible || 0;
    document.getElementById('stat-filtered').textContent = stats.filtered_out || 0;
    document.getElementById('stat-recommended').textContent = matches.length;

    // Update filter summary
    const filterTags = document.getElementById('filter-tags');
    if (filterTags && Object.keys(filterSummary).length > 0) {
        filterTags.innerHTML = Object.entries(filterSummary)
            .map(([reason, count]) => `<span class="filter-tag">${count} ${reason}</span>`)
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
                            <h3>${match.display_name}</h3>
                            <span class="badge badge-role">${match.preferred_role}</span>
                        </div>
                        <div class="pick-details">
                            <div class="detail-item">
                                <span class="detail-icon">📍</span>
                                <span>${match.city}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-icon">📧</span>
                                <span>${match.contact_info}</span>
                            </div>
                            ${match.shared_languages && match.shared_languages.length > 0 ? `
                                <div class="detail-item">
                                    <span class="detail-icon">🗣️</span>
                                    <span>${match.shared_languages.join(', ')}</span>
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
                            <strong>Why:</strong> ${match.reason}
                        </div>
                        <div class="pick-actions">
                            <a href="mailto:${match.contact_info}" class="btn btn-sm btn-secondary">
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
